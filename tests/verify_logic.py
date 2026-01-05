import sys
import unittest
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.calculations import calculate_tension, calculate_compression, calculate_bolt_shear
from core.profiles import ProfileDatabase

class TestCore(unittest.TestCase):
    def test_database(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'profiles.csv')
        db = ProfileDatabase(db_path)
        self.assertTrue(len(db.profiles) > 0)
        p = db.get_profile("WF 200x100")
        self.assertIsNotNone(p)
        self.assertEqual(p.d, 200)

    def test_tension(self):
        # A36 Steel (Fy=250, Fu=400)
        # Ag = 1000 mm2
        res = calculate_tension(1000, 1000, 250, 400)
        self.assertEqual(res['yield']['Pn'], 250000)
        self.assertEqual(res['yield']['phi_Pn'], 0.9 * 250000)

    def test_connection_shear(self):
        # 1 bolt, db=16, Fnv=372
        res = calculate_bolt_shear(16, 1, 372)
        expected_Ab = 0.25 * 3.1415926535 * 16**2
        self.assertAlmostEqual(res['Ab'], expected_Ab, places=2)
        self.assertTrue(res['Rn'] > 0)

    def test_flexure(self):
        # Test basic Mp calculation
        # WF 200x100
        # Zx = 184000 mm3
        # Fy = 250 MPa
        # Mp = 184000 * 250 = 46,000,000 Nmm
        db = ProfileDatabase('data/profiles.csv')
        p = db.get_profile("WF 200x100")
        
        # Lb=0 -> Should be Mp
        from core.calculations import calculate_flexure
        res = calculate_flexure(p, 0, 1.0, 250)
        
        expected_Mp = p.Zx * 250
        self.assertAlmostEqual(res['Mn'], expected_Mp, places=0)
        self.assertEqual(res['state'], "Yielding (Lb <= Lp)")

    def test_weld(self):
        # Test Fillet Weld
        # a = 6mm, L = 100mm, Fexx = 490 (E70xx)
        # phi = 0.75
        # Rn = 0.6 * Fexx * (0.707 * a) * L
        from core.calculations import calculate_weld
        res = calculate_weld("Fillet", 490, 6, 100)
        
        expected_Rn = 0.6 * 490 * (0.707 * 6) * 100
        self.assertAlmostEqual(res['Rn'], expected_Rn, places=1)
        self.assertEqual(res['phi'], 0.75)

    def test_combined(self):
        # Test Interaction Equation
        # WF 200x100
        db = ProfileDatabase('data/profiles.csv')
        p = db.get_profile("WF 200x100")
        
        # Determine Capacity first
        from core.calculations import calculate_compression, calculate_flexure, calculate_combined
        
        # Situation: Small Axial, Large Moment (Pr < 0.2)
        # Low Pu puts us in Eq H1-1b
        L = 3000
        Fy = 250
        res = calculate_combined(p, Pu=1000, Mux=10000000, Muy=0, L=L, K=1.0, Cb=1.0, Fy=Fy)
        
        self.assertTrue(res['Pr'] < 0.2)
        self.assertTrue("H1-1b" in res['eq'])
        
        # Situation: Large Axial (Pr >= 0.2)
        # High Pu puts us in Eq H1-1a
        res_high_p = calculate_combined(p, Pu=400000, Mux=1000000, Muy=0, L=L, K=1.0, Cb=1.0, Fy=Fy)
        self.assertTrue(res_high_p['Pr'] >= 0.2)
        self.assertTrue("H1-1a" in res_high_p['eq'])

    def test_base_plate(self):
        # Test Base Plate
        # Pu = 500 kN, fc = 25 MPa
        # Column WF 200x200 (assume d=200, bf=200)
        # B = 400, N = 400
        
        from core.calculations import calculate_base_plate
        
        Pu = 500000
        fc = 25
        B = 400
        N = 400
        d = 200
        bf = 200
        
        res = calculate_base_plate(Pu, fc, B, N, d, bf)
        
        # Phi Pp = 0.65 * 0.85 * fc * A1
        expected_phi_Pp = 0.65 * 0.85 * fc * (B * N)
        self.assertAlmostEqual(res['phi_Pp'], expected_phi_Pp, places=1)
        self.assertTrue(res['bearing_ratio'] <= 1.0)
        
        # t_req check
        # m = (N - 0.95d) / 2 = (400 - 190) / 2 = 105
        # n = (B - 0.8bf) / 2 = (400 - 160) / 2 = 120
        # l = 120
        # treq = 120 * sqrt(2*500000 / (0.9*250*160000))
        # treq = 120 * sqrt(1000000 / 36000000) = 120 * sqrt(0.0277) = 120 * 0.166 = ~20mm
        self.assertGreater(res['t_req'], 10)

    def test_moment_plate(self):
        # Test Moment End Plate
        # Mu = 50 kNm, Bolt 16mm, n=4, thick=20
        # Beam WF 200x100
        from core.calculations import calculate_moment_plate
        from core.profiles import ProfileDatabase
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'profiles.csv')
        db = ProfileDatabase(db_path)
        profile = db.get_profile("WF 200x100")
        
        Mu = 40
        d_bolt = 16
        n_bolts = 4
        thick = 20
        
        res = calculate_moment_plate(Mu, d_bolt, n_bolts, thick, profile)
        
        # Check integrity
        self.assertEqual(res['status'], "OK")
        self.assertEqual(res['plate_check'], "OK")
        self.assertTrue(res['bolt_ratio'] < 1.0)
        
if __name__ == '__main__':
    unittest.main()
