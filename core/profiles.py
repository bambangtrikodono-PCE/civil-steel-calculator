import csv
import os

class SteelProfile:
    def __init__(self, name, weight, depth, width, web_thick, flange_thick, area, ix, iy, rx, ry, zx, zy):
        self.name = name
        self.weight = float(weight)  # kg/m
        self.d = float(depth)        # mm
        self.bf = float(width)       # mm
        self.tw = float(web_thick)   # mm
        self.tf = float(flange_thick)# mm
        self.Ag = float(area) * 100  # cm2 -> mm2 (Input is cm2)
        self.Ix = float(ix) * 10000  # cm4 -> mm4
        self.Iy = float(iy) * 10000  # cm4 -> mm4
        self.rx = float(rx) * 10     # cm -> mm
        self.ry = float(ry) * 10     # cm -> mm
        self.Zx = float(zx) * 1000   # cm3 -> mm3
        self.Zy = float(zy) * 1000   # cm3 -> mm3
        
        # Flexural Properties (Derived)
        self.Sx = self.Ix / (self.d / 2)
        self.Sy = self.Iy / (self.bf / 2)
        
        # Torsion Properties (Approximate)
        # h0 = distance between flange centroids
        self.h0 = self.d - self.tf
        
        # J = Sum(b*t^3/3)
        # 2 Flanges + 1 Web
        self.J = (2 * self.bf * self.tf**3 + (self.d - 2*self.tf) * self.tw**3) / 3
        
        # Cw (Warping Constant) approx for I-shape = Iy * h0^2 / 4
        self.Cw = (self.Iy * self.h0**2) / 4
        
        # rts used for LTB = sqrt(sqrt(Iy * Cw) / Sx)
        # Simplified approximate: rts ~ ry / sqrt(1 + 1/6 * (h * tw) / (bf * tf)) ?
        # Or exact formula: rts^2 = sqrt(Iy * Cw) / Sx
        import math
        try:
           self.rts = math.sqrt(math.sqrt(self.Iy * self.Cw) / self.Sx)
        except ValueError:
           self.rts = self.ry # Fallback

    def __repr__(self):
        return f"<SteelProfile {self.name}>"

class ProfileDatabase:
    def __init__(self, csv_path):
        self.profiles = []
        self._load_data(csv_path)

    def _load_data(self, csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Database file not found: {csv_path}")
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == 'WF':
                    self.profiles.append(SteelProfile(
                        row['name'], row['weight_kg_m'], row['depth_mm'], row['width_mm'],
                        row['web_thick_mm'], row['flange_thick_mm'], row['area_cm2'],
                        row['ix_cm4'], row['iy_cm4'], row['rx_cm'], row['ry_cm'],
                        row['zx_cm3'], row['zy_cm3']
                    ))

    def get_all_names(self):
        return [p.name for p in self.profiles]

    def get_profile(self, name):
        for p in self.profiles:
            if p.name == name:
                return p
        return None
