"""T1 candidate triplet motion: source-clock, branch, and stationary controls."""
import importlib.util,sys,unittest,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_t1_triplet_motion_diagnostic.py"
spec=importlib.util.spec_from_file_location("t1_triplet_diagnostic",P)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

def node(i,x,y=10,ms=None,group=1,role="main",uid=None,spatial=True):
 return {"uid":uid or f"{role}:{i}:{x}", "role":role,"group":group,
         "ordinal":i,"time_ms":i*1000 if ms is None else ms,
         "centroid_x":float(x),"centroid_y":float(y),"spatial_supported":spatial}
def edge(a,b):return {"src":a["uid"],"dst":b["uid"]}

class TripletTests(unittest.TestCase):
 def test_constant_velocity_zero_jump(self):
  a,b,c=node(0,5),node(1,10),node(2,15)
  r=m.triplet_kinematics(a,b,c)
  self.assertAlmostEqual(r["first_speed_px_per_s"],5)
  self.assertAlmostEqual(r["velocity_jump_px_per_s"],0)
  self.assertAlmostEqual(r["turning_angle_degrees_or_null"],0)
  self.assertEqual(r["elapsed_ms_bc"],1000)

 def test_direction_turn_90(self):
  a,b,c=node(0,10,y=10),node(1,20,y=10),node(2,20,y=20)
  r=m.triplet_kinematics(a,b,c)
  self.assertAlmostEqual(r["turning_angle_degrees_or_null"],90,places=10)
  self.assertGreater(r["velocity_jump_px_per_s"],10)

 def test_stationary_artifact_is_not_physically_validated(self):
  a,b,c=node(0,10),node(1,10),node(2,10)
  r=m.triplet_kinematics(a,b,c)
  self.assertEqual(r["velocity_jump_ratio_diagnostic"],0)
  self.assertIsNone(r["turning_angle_degrees_or_null"])
  v=m.analyze_triplet_graph([a,b,c],[edge(a,b),edge(b,c)])
  self.assertEqual(v["near_stationary_paths"],1)
  self.assertEqual(v["candidate_two_edge_paths"],1)
  self.assertFalse(r["physical_plume_lineage_verified"])

 def test_split_multiple_middle_paths_not_pruned(self):
  a=node(0,10); b=node(1,15);c1=node(2,20);c2=node(2,27,uid="c2")
  e=[edge(a,b),edge(b,c1),edge(b,c2)]
  r=m.analyze_triplet_graph([a,b,c1,c2],e)
  self.assertEqual(r["candidate_two_edge_paths"],2)
  self.assertEqual(r["multi_parent_or_child_middle_paths"],2)
  self.assertEqual(len(e),3)
  self.assertTrue(r["no_plume_mask_changes"])

 def test_merge_two_predecessors(self):
  a=node(0,5);aa=node(0,8,uid="a2")
  b=node(1,10);c=node(2,15)
  r=m.analyze_triplet_graph([a,aa,b,c],[edge(a,b),edge(aa,b),edge(b,c)])
  self.assertEqual(r["candidate_two_edge_paths"],2)
  self.assertEqual(r["multi_parent_or_child_middle_paths"],2)

 def test_clock_1001_ms_velocity_handled(self):
  a=node(0,0,ms=0);b=node(1,10,ms=1001);c=node(2,20,ms=2001)
  r=m.triplet_kinematics(a,b,c)
  self.assertEqual(r["elapsed_ms_ab"],1001)
  self.assertAlmostEqual(r["first_speed_px_per_s"],10/1.001)
  self.assertAlmostEqual(r["second_speed_px_per_s"],10)

 def test_source_gaps_and_cross_stream_refused(self):
  a,b,c=node(0,5),node(1,10),node(3,15)
  with self.assertRaises(ValueError):
   m.triplet_kinematics(a,b,c)
  with self.assertRaises(ValueError):
   m.triplet_kinematics(a,b,node(2,15,group=2))
  with self.assertRaises(ValueError):
   m.analyze_triplet_graph([a,c],[edge(a,c)])

 def test_invalid_elapsed_interval_refused(self):
  a,b,c=node(0,5),node(1,10,ms=2500),node(2,15,ms=3500)
  with self.assertRaisesRegex(ValueError,"time"):
   m.triplet_kinematics(a,b,c)

 def test_bad_motion_input_rejected(self):
  a,b,c=node(0,5),node(1,10),node(2,15)
  with self.assertRaises(ValueError):
   m.triplet_kinematics(a,b,node(2,float("nan")))
  with self.assertRaises(ValueError):
   m.triplet_kinematics(a,b,c,direction_min_speed_px_s=0)

 def test_no_original_node_or_edge_mutation(self):
  a,b,c=node(0,5),node(1,10),node(2,15)
  e=[edge(a,b),edge(b,c)]
  old=[x.copy() for x in (a,b,c)]
  copy=[x.copy() for x in e]
  m.analyze_triplet_graph([a,b,c],e)
  self.assertEqual([a,b,c],old);self.assertEqual(e,copy)

 def test_missing_duplicate_nodes_refused(self):
  a,b,c=node(0,5),node(1,10),node(2,15)
  with self.assertRaises(ValueError):
   m.analyze_triplet_graph([a,a,b,c],[edge(a,b),edge(b,c)])
  with self.assertRaises(ValueError):
   m.analyze_triplet_graph([a,b],[edge(a,b),{"src":b["uid"],"dst":"missing"}])

if __name__=="__main__":unittest.main()
