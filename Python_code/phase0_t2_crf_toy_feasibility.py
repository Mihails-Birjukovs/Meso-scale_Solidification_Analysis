"""T2 CRF/factor-graph feasibility TOY: exact enumeration for <=8 component nodes.

NOT for experimental Ga-In data, NOT calibrated, NOT a scalable optimizer.
Tiny explicit discrete energy helps test whether T2 merits a future real pilot.
"""
from __future__ import annotations
from itertools import product
import math

LABELS=("plume_like","artifact_like","uncertain")
SCHEMA="ga-in-t2-component-crf-synthetic-feasibility/v0.1"

def exact_toy_inference(unary:list[dict[str,float]], temporal_edges:list[tuple[int,int,float]],
                        labels:tuple[str,...]=LABELS)->dict:
    n=len(unary)
    if not 1<=n<=8:
        raise ValueError("Toy enumeration permitted only for 1..8 nodes")
    if len(set(labels))!=len(labels) or len(labels)<2:
        raise ValueError("Need distinct label states")
    for j,cost in enumerate(unary):
        if set(cost)!=set(labels) or any(not math.isfinite(float(v)) for v in cost.values()):
            raise ValueError(f"Bad unary evidence for node {j}")
    for i,j,w in temporal_edges:
        if not (0<=i<n and 0<=j<n and i!=j and math.isfinite(w) and w>=0):
            raise ValueError("Invalid pairwise association edge")
    options=[]
    for z in product(labels,repeat=n):
        energy=sum(float(unary[i][z[i]]) for i in range(n))
        energy+=sum(float(w)*(z[i]!=z[j]) for i,j,w in temporal_edges)
        options.append((z,energy))
    min_e=min(e for z,e in options)
    scaled=[math.exp(-(e-min_e)) for z,e in options]
    norm=sum(scaled)
    best=next((z,e) for z,e in options if abs(e-min_e)<1e-12)
    marginals=[{name:0.0 for name in labels} for _ in range(n)]
    for (z,e),weight in zip(options,scaled):
        for i,label in enumerate(z):
            marginals[i][label]+=weight/norm
    return {
        "schema":SCHEMA,
        "evidence_status":"SYNTHETIC_TOY_NOT_CALIBRATED_NOT_EXPERIMENTAL",
        "nodes":n,"assignments_enumerated":len(options),
        "map_labels":list(best[0]),"map_energy":best[1],
        "log_partition":-min_e+math.log(norm),
        "marginals":marginals,
    }
