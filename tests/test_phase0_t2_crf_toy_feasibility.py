"""T2 toy exact enumeration falsification tests, standalone standard Python."""
import importlib.util
import sys
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_t2_crf_toy_feasibility.py"
spec=importlib.util.spec_from_file_location("toy_crf",P)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class CRFToyTests(unittest.TestCase):
    def f(self):
        return [{"plume_like":.2,"artifact_like":2.0,"uncertain":2.5},
                {"plume_like":1.1,"artifact_like":.2,"uncertain":2.5}]
    def test_no_edge_independent_unary(self):
        r=m.exact_toy_inference(self.f(),[])
        self.assertEqual(r["map_labels"],["plume_like","artifact_like"])
    def test_good_link_can_rescue_ambiguous_component(self):
        r=m.exact_toy_inference(self.f(),[(0,1,1.0)])
        self.assertEqual(r["map_labels"],["plume_like","plume_like"])
        self.assertEqual(r["assignments_enumerated"],9)
    def test_marginals_are_normalized_not_same_as_map(self):
        r=m.exact_toy_inference(self.f(),[(0,1,1.0)])
        for margs in r["marginals"]:
            self.assertAlmostEqual(sum(margs.values()),1.0,places=12)
            self.assertTrue(all(0.0<v<1.0 for v in margs.values()))
    def test_stationary_artifact_unary_can_win(self):
        data=[{"plume_like":3,"artifact_like":0,"uncertain":2},
              {"plume_like":3,"artifact_like":0,"uncertain":2}]
        r=m.exact_toy_inference(data,[(0,1,2)])
        self.assertEqual(r["map_labels"],["artifact_like","artifact_like"])
    def test_dangerous_false_link_can_propagate_wrong_label(self):
        base=self.f()
        no_link=m.exact_toy_inference(base,[])
        with_link=m.exact_toy_inference(base,[(0,1,1.0)])
        self.assertNotEqual(no_link["map_labels"],with_link["map_labels"])
    def test_reject_invalid_edges(self):
        with self.assertRaises(ValueError):
            m.exact_toy_inference(self.f(),[(0,5,1.0)])
    def test_reject_large_graph(self):
        with self.assertRaises(ValueError):
            m.exact_toy_inference([self.f()[0]]*9,[])
if __name__=="__main__":
    unittest.main()
