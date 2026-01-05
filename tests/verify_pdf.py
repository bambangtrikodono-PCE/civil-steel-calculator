import unittest
import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reports import PDFReport

class TestPDFReport(unittest.TestCase):
    def test_generate_pdf(self):
        filename = "test_report.pdf"
        title = "Test Calculation"
        inputs = {"Load": "100 kN", "Length": "3000 mm"}
        results = {"Capacity": "150 kN", "Ratio": "0.66", "status": "SAFE"}
        
        PDFReport.generate(filename, title, inputs, results)
        
        # Check if file exists
        self.assertTrue(os.path.exists(filename))
        
        # Check if size > 0
        self.assertGreater(os.path.getsize(filename), 0)
        
        # Cleanup
        try:
            os.remove(filename)
        except:
            pass

    def test_imports(self):
        # Verify views.py imports correctly (no syntax errors or circular imports)
        try:
            from gui.views import BaseView
        except ImportError as e:
            self.fail(f"Import failed: {e}")

if __name__ == '__main__':
    unittest.main()
