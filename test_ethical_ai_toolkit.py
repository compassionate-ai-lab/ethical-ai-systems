"""Meaningful regression tests for the book's policy examples."""
import unittest
from decimal import Decimal
from math import nan, inf
from ethical_ai_toolkit import *

class ToolkitTests(unittest.TestCase):
    def test_composite_matches_book(self):
        example = dict(zip(INDEX_WEIGHTS,
            [55, 71, 62, 83, 58, 74, 66, 80, 70, 52]))
        self.assertEqual(composite(example), 66.64)
        self.assertFalse(Assessment(example).release)

    def test_mandatory_gates_override_high_scores(self):
        scores = {k:90 for k in INDEX_WEIGHTS}
        self.assertFalse(Assessment(scores).release)
        self.assertFalse(Assessment(scores,
            evidence_complete=True).release)
        self.assertTrue(Assessment(scores, evidence_complete=True,
            mandatory_gates_passed=True).release)
        scores['oversight']=39
        self.assertFalse(Assessment(scores,evidence_complete=True,
            mandatory_gates_passed=True).release)

    def test_missing_is_different_from_approved_na(self):
        scores={k:90 for k in INDEX_WEIGHTS if k!='augmentation'}
        with self.assertRaises(ValueError):composite(scores)
        self.assertEqual(composite(scores,('augmentation',)),90)
        with self.assertRaises(ValueError):composite({},tuple(INDEX_WEIGHTS))

    def test_scores_reject_nonfinite_and_boolean(self):
        for bad in (nan,inf,-1,101,True,'90'):
            scores={k:90 for k in INDEX_WEIGHTS};scores['bias']=bad
            with self.assertRaises(ValueError):composite(scores)

    def test_autonomy_is_monotone_with_harm_and_irreversibility(self):
        for impact in range(3):
            values=[allowed_rung(impact,r) for r in range(3)]
            self.assertEqual(values,sorted(values,reverse=True))
        for rev in range(3):
            values=[allowed_rung(i,rev) for i in range(3)]
            self.assertEqual(values,sorted(values,reverse=True))
        self.assertEqual([allowed_rung(2,r) for r in range(3)],[1,1,1])
        self.assertEqual(allowed_rung(0,0),4)
        for bad in (-1,5,True,2.0):
            with self.assertRaises(ValueError):permits(bad,0,0)

    def test_budget_is_cumulative_and_retry_does_not_execute(self):
        e=Envelope('100.00',['supplier'],'80')
        self.assertTrue(e.authorise('a','60','supplier')['allowed'])
        self.assertFalse(e.authorise('a','60','supplier')['allowed'])
        self.assertFalse(e.authorise('b','60','supplier')['allowed'])
        self.assertEqual(e.spent,Decimal('60'))
        with self.assertRaises(ValueError):e.authorise('a','61','supplier')

    def test_authority_and_exact_decimal_amounts(self):
        e=Envelope('1.00',['supplier'],'0.20')
        self.assertFalse(e.authorise('a','.30','supplier')['allowed'])
        self.assertTrue(e.authorise('a','.30','supplier',confirmed=True)['allowed'])
        self.assertFalse(e.authorise('b','.10','unknown')['allowed'])
        self.assertFalse(e.authorise('c','.10','supplier',shares_identity=True)['allowed'])
        e.revoked=True
        self.assertFalse(e.authorise('d','.10','supplier')['allowed'])
        for bad in ('NaN','Infinity','-.01','.001',True):
            with self.assertRaises(ValueError):money(bad)

    def test_fairness_has_explicit_undefined_groups(self):
        y=[1,1,0,0,1,1,1,0]; p=[1,1,0,0,0,1,0,0]
        g=['A']*4+['B']*4
        self.assertAlmostEqual(equal_opportunity_gap(y,p,g),2/3)
        self.assertEqual(demographic_parity_difference(p,g),.25)
        self.assertIsNone(true_positive_rates([1,0],[1,0],['A','B'])['B'])
        with self.assertRaises(ValueError):equal_opportunity_gap([1,0],[1,0],['A','B'])
        for bad in ([],[2],[True]):
            with self.assertRaises(ValueError):selection_rates(bad,['A']*len(bad))

    def test_calibration_counts_all_samples_and_validates(self):
        r=calibration_by_group([0,1,.5],[0,1,1],['A']*3,bins=2)
        self.assertEqual(sum(v['count'] for v in r.values()),3)
        self.assertEqual(r['A:bin1']['mean_score'],.75)
        for bad in (0,-1,True,2.5):
            with self.assertRaises(ValueError):calibration_by_group([.5],[1],['A'],bad)
        with self.assertRaises(ValueError):calibration_by_group([nan],[1],['A'])

    def test_metadata_cannot_overwrite_authoritative_fields(self):
        r=ActionRecord('a','2026-10-29T00:00:00Z','agent','owner',
                       'tool','permission','effect','v1',
                       metadata={'action_id':'forged'})
        self.assertTrue(r.is_complete())
        self.assertEqual(r.as_dict()['action_id'],'a')
        r.actor=' '
        self.assertFalse(r.is_complete())

if __name__=='__main__':unittest.main()
