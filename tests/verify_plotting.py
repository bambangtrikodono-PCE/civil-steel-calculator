import unittest
import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.profiles import ProfileDatabase
from core.plotting import create_section_plot
import matplotlib.figure

class TestPlotting(unittest.TestCase):
    def test_create_plot(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'profiles.csv')
        db = ProfileDatabase(db_path)
        profile = db.get_profile("WF 200x100")
        
        fig = create_section_plot(profile)
        
        # Check if it returns a Figure
        self.assertIsInstance(fig, matplotlib.figure.Figure)
        
        # Check if it has axes
        self.assertTrue(len(fig.axes) > 0)
        
        # Check title
        ax = fig.axes[0]
        self.assertEqual(ax.get_title(), f"Section: {profile.name}")

if __name__ == '__main__':
    unittest.main()
