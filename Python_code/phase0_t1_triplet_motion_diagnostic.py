"""T1 three-frame candidate lineage motion-consistency diagnostic.

A component path A->B->C from two frozen original-source-adjacent T1
edges is not necessarily one physical plume. No path is deleted, accepted,
fitted or assigned probability. Stationary sensor defects can exhibit
perfect zero-acceleration consistency; split/merge centroids can mislead.

Source input: public-shaped v0.1 component/association JSON dicts.
"""
from __future__ import annotations
import math
from collections import defaultdict

SCHEMA="ga-in-t1-three-frame-motion-consistency/v0.1.0"

def triplet_kinematics(a:dict,b:dict,c:dict,*,direction_min_speed_px_s:float=1.0)->dict:
    """Compute source-time-aware, original-source-coordinate two-step motion."""
    if any(x["role"]!=a["role"] or x["group"]!=a["group"] for x in (b,c)):
        raise ValueError("cross-acquisition candidate triplet")
    if not (b["ordinal"]==a["ordinal"]+1 and c["ordinal"]==b["ordinal"]+1):
        raise ValueError("triplet must use adjacent original-source ordinals")
    dt1=(b["time_ms"]-a["time_ms"])/1000.
    dt2=(c["time_ms"]-b["time_ms"])/1000.
    if not 0<dt1<=1.5 or not 0<dt2<=1.5:
        raise ValueError("unvalidated source time increment")
    if not math.isfinite(direction_min_speed_px_s) or direction_min_speed_px_s<=0:
        raise ValueError("invalid minimum speed")
    yx=[]
    for z in (a,b,c):
        point=[float(z["centroid_y"]),float(z["centroid_x"])]
        if any(not math.isfinite(v) for v in point):
            raise ValueError("nonfinite original-detector component coordinate")
        yx.append(point)
    v1=[(yx[1][k]-yx[0][k])/dt1 for k in (0,1)]
    v2=[(yx[2][k]-yx[1][k])/dt2 for k in (0,1)]
    speed1=math.hypot(*v1)
    speed2=math.hypot(*v2)
    delta=math.hypot(*(v2[k]-v1[k] for k in (0,1)))
    # Same time horizon for static/moving; not an acceleration uncertainty
    # model. Units: detector pixel/s^2 (each step's velocity difference).
    temporal_acceleration=2*delta/(dt1+dt2)
    ratio=delta/max(speed1,speed2,direction_min_speed_px_s)
    angle=None
    if speed1>=direction_min_speed_px_s and speed2>=direction_min_speed_px_s:
        dot=sum(v1[k]*v2[k] for k in (0,1))
        angle=math.degrees(math.acos(max(-1.0,min(1.0,dot/(speed1*speed2)))))
    net=math.hypot(yx[2][0]-yx[0][0],yx[2][1]-yx[0][1])
    return {
        "source_a":a["uid"],"source_b":b["uid"],"source_c":c["uid"],
        "elapsed_ms_ab":b["time_ms"]-a["time_ms"],
        "elapsed_ms_bc":c["time_ms"]-b["time_ms"],
        "first_speed_px_per_s":speed1,"second_speed_px_per_s":speed2,
        "velocity_jump_px_per_s":delta,
        "time_symmetric_accel_px_per_s2":temporal_acceleration,
        "velocity_jump_ratio_diagnostic":ratio,
        "turning_angle_degrees_or_null":angle,
        "net_displacement_2frames_px":net,
        "stationary_detector_artifact_not_excluded":True,
        "independent_velocity_validation":False,
        "physical_plume_lineage_verified":False,
    }

def analyze_triplet_graph(nodes:list[dict],edges:list[dict],*,
                          direction_min_speed_px_s:float=1.0,
                          stationary_speed_px_s:float=.5,
                          high_angle_deg:float=120.,
                          max_report_examples:int=12)->dict:
    """Aggregate all two-edge candidate paths without pruning.

    Number of paths can scale as sum(deg_in(B)*deg_out(B)); keep only
    aggregated QA counters and limited source UIDs for manual review.
    """
    if stationary_speed_px_s<0 or not math.isfinite(stationary_speed_px_s):
        raise ValueError("invalid stationary threshold")
    if not 0<=high_angle_deg<=180 or not math.isfinite(high_angle_deg):
        raise ValueError("invalid angle threshold")
    if max_report_examples<0 or max_report_examples>100:
        raise ValueError("invalid review cap")
    indexed={x["uid"]:x for x in nodes}
    if len(indexed)!=len(nodes):raise ValueError("duplicate source component UID")
    parents=defaultdict(list);children=defaultdict(list)
    for e in edges:
        a=e["src"];b=e["dst"]
        if a not in indexed or b not in indexed:
            raise ValueError("candidate edge references missing source component")
        x=indexed[a];y=indexed[b]
        if x["role"]!=y["role"] or x["group"]!=y["group"] or y["ordinal"]!=x["ordinal"]+1:
            raise ValueError("candidate edge bridges original acquisition discontinuity")
        parents[b].append(a)
        children[a].append(b)
    counters={"candidate_two_edge_paths":0,"motion_orientation_defined":0,
              "near_stationary_paths":0,"high_angle_paths":0,
              "spatially_kept_triplet_paths":0,"multi_parent_or_child_middle_paths":0}
    examples=[]
    velocity_jumps=[]
    turns=[]
    for middle in indexed:
        for aa in parents[middle]:
            for cc in children[middle]:
                z=triplet_kinematics(indexed[aa],indexed[middle],indexed[cc],
                                    direction_min_speed_px_s=direction_min_speed_px_s)
                counters["candidate_two_edge_paths"]+=1
                stationary=(z["first_speed_px_per_s"]<stationary_speed_px_s and
                            z["second_speed_px_per_s"]<stationary_speed_px_s)
                counters["near_stationary_paths"]+=stationary
                turn=z["turning_angle_degrees_or_null"]
                if turn is not None:
                    counters["motion_orientation_defined"]+=1
                    turns.append(turn)
                if turn is not None and turn>=high_angle_deg:
                    counters["high_angle_paths"]+=1
                keep=bool(indexed[aa].get("spatial_supported")) and \
                     bool(indexed[middle].get("spatial_supported")) and \
                     bool(indexed[cc].get("spatial_supported"))
                counters["spatially_kept_triplet_paths"]+=keep
                multiple=(len(parents[middle])>1 or len(children[middle])>1)
                counters["multi_parent_or_child_middle_paths"]+=multiple
                velocity_jumps.append(z["velocity_jump_ratio_diagnostic"])
                # These are descriptive review examples, NOT confirmed false
                # links, true turns, sensor artifacts, or true plume tracks.
                if len(examples)<max_report_examples and (
                      stationary or (turn is not None and turn>=high_angle_deg)):
                    examples.append({
                        "source_a":aa,"source_b":middle,"source_c":cc,
                        "reason":"near-stationary" if stationary else "large-turn",
                        "turn_degrees":turn,
                        "velocity_jump_ratio":z["velocity_jump_ratio_diagnostic"],
                        "geometry_and_source_timing_only":True
                    })
    def quartiles(vals):
        if not vals:return None
        v=sorted(vals)
        return {str(q):v[min(len(v)-1,int(q*(len(v)-1)))] for q in (0,.25,.5,.75,.9,1)}
    return {
        "schema":SCHEMA,
        "status":"CANDIDATE_TRIPLET_KINEMATICS_NOT_TRUE_PHYSICAL_LINEAGE",
        "parameters":{
           "direction_min_speed_px_s":direction_min_speed_px_s,
           "stationary_speed_px_s":stationary_speed_px_s,
           "high_angle_deg":high_angle_deg
        },
        **counters,
        "velocity_jump_ratio_quantiles":quartiles(velocity_jumps),
        "turning_angle_defined_only_quantiles_deg":quartiles(turns),
        "limited_review_examples":examples,
        "no_plume_mask_changes":True,
        "counterexamples":[
            "Stationary image defect produces zero velocity jump and would look maximally coherent",
            "Genuine plume U-turn or split/merge may cause very high apparent centroid-velocity jump",
            "Geometric candidate graph allows alternative simultaneous paths through the same middle node",
            "Source-time candidate ticks are not independently certified physical timestamps"
        ],
    }
