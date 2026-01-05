import customtkinter as ctk
import sys
import os

# Ensure we can import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.calculations import calculate_tension, calculate_compression, calculate_bolt_shear
from core.profiles import ProfileDatabase
from core.reports import PDFReport
from tkinter import filedialog

class BaseView(ctk.CTkScrollableFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(20, weight=1) # Spacer at bottom

        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.db = ProfileDatabase(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'profiles.csv'))
        self.profiles = self.db.get_all_names()
        
        self.last_inputs = {}
        self.last_results = {}
        
        self.export_btn = ctk.CTkButton(self, text="Export PDF Report", command=self.export_pdf, state="disabled", fg_color="green")
        self.export_btn.grid(row=30, column=0, padx=20, pady=(0, 20), sticky="ew")

    def export_pdf(self):
        if not self.last_results:
            return
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if filename:
            PDFReport.generate(filename, self.title_label.cget("text"), self.last_inputs, self.last_results)

class TensionView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Tension Member Calculator (SNI 1729)", **kwargs)

        # Profile Selection
        self.profile_label = ctk.CTkLabel(self, text="Select Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Material Properties
        self.fy_label = ctk.CTkLabel(self, text="Yield Strength, Fy (MPa):")
        self.fy_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fy_entry = ctk.CTkEntry(self, placeholder_text="240")
        self.fy_entry.insert(0, "240")
        self.fy_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.fu_label = ctk.CTkLabel(self, text="Ultimate Strength, Fu (MPa):")
        self.fu_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fu_entry = ctk.CTkEntry(self, placeholder_text="370")
        self.fu_entry.insert(0, "370")
        self.fu_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate Button
        self.calc_btn = ctk.CTkButton(self, text="Calculate Capacity", command=self.calculate)
        self.calc_btn.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

        # Result Display
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=8, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            fy = float(self.fy_entry.get())
            fu = float(self.fu_entry.get())

            # Simplification: Ae = Ag (no shear lag deduction yet)
            res = calculate_tension(profile.Ag, profile.Ag, fy, fu)
            
            self.last_inputs = {
                "Profile": profile_name,
                "Yield Strength (Fy)": f"{fy} MPa",
                "Ultimate Strength (Fu)": f"{fu} MPa"
            }
            self.last_results = {
                "Yield Capacity": f"{res['yield']['phi_Pn']/1000:.2f} kN",
                "Rupture Capacity": f"{res['rupture']['phi_Pn']/1000:.2f} kN",
                "Design Strength": f"{res['phi_Pn']/1000:.2f} kN",
                "status": "Calculated"
            }
            self.export_btn.configure(state="normal")
            
            output = f"Profile: {profile.name}\n"
            output += f"Area (Ag): {profile.Ag} mm2\n"
            output += "-"*30 + "\n"
            output += f"Yield Capacity (Phi_Pn): {res['yield']['phi_Pn']/1000:.2f} kN\n"
            output += f"Rupture Capacity (Phi_Pn): {res['rupture']['phi_Pn']/1000:.2f} kN\n"
            output += "-"*30 + "\n"
            output += f"DESIGN STRENGTH: {res['phi_Pn']/1000:.2f} kN\n"
            
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class CompressionView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Compression Member Calculator", **kwargs)

        # Profile Selection
        self.profile_label = ctk.CTkLabel(self, text="Select Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Length Input
        self.len_label = ctk.CTkLabel(self, text="Unbraced Length, L (mm):")
        self.len_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.len_entry = ctk.CTkEntry(self, placeholder_text="3000")
        self.len_entry.insert(0, "3000")
        self.len_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # K factor
        self.k_label = ctk.CTkLabel(self, text="Effective Length Factor, K:")
        self.k_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.k_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.k_entry.insert(0, "1.0")
        self.k_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Fy
        self.fy_label = ctk.CTkLabel(self, text="Yield Strength, Fy (MPa):")
        self.fy_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fy_entry = ctk.CTkEntry(self, placeholder_text="240")
        self.fy_entry.insert(0, "240")
        self.fy_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Capacity", command=self.calculate)
        self.calc_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=10, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            L = float(self.len_entry.get())
            K = float(self.k_entry.get())
            fy = float(self.fy_entry.get())

            res = calculate_compression(profile.Ag, profile.rx, profile.ry, K, L, K, L, fy)

            self.last_inputs = {
                "Profile": profile_name,
                "Length (L)": f"{L} mm",
                "K Factor": K,
                "Yield Strength (Fy)": f"{fy} MPa"
            }
            self.last_results = {
                "KL/r": f"{res['KL_r']:.2f}",
                "Critical Stress (Fcr)": f"{res['Fcr']:.2f} MPa",
                "Design Strength": f"{res['phi_Pn']/1000:.2f} kN",
                "status": "Calculated"
            }
            self.export_btn.configure(state="normal")

            output = f"Profile: {profile.name}\n"
            output += f"Area: {profile.Ag} mm2, rx: {profile.rx} mm, ry: {profile.ry} mm\n"
            output += f"KL/r: {res['KL_r']:.2f}\n"
            output += f"Elastic Buckling (Fe): {res['Fe']:.2f} MPa\n"
            output += f"Critical Stress (Fcr): {res['Fcr']:.2f} MPa\n"
            output += "-"*30 + "\n"
            output += f"DESIGN STRENGTH (Phi_Pn): {res['phi_Pn']/1000:.2f} kN\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class ConnectionView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Bolt Connection Calculator", **kwargs)

        # Bolt Diameter
        self.db_label = ctk.CTkLabel(self, text="Bolt Diameter, db (mm):")
        self.db_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.db_entry = ctk.CTkEntry(self, placeholder_text="16")
        self.db_entry.insert(0, "16")
        self.db_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Number of Bolts
        self.n_label = ctk.CTkLabel(self, text="Number of Bolts, n:")
        self.n_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.n_entry = ctk.CTkEntry(self, placeholder_text="4")
        self.n_entry.insert(0, "4")
        self.n_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Shear Strength Fnv
        self.fnv_label = ctk.CTkLabel(self, text="Nominal Shear Stress, Fnv (MPa):")
        self.fnv_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fnv_entry = ctk.CTkEntry(self, placeholder_text="372")
        self.fnv_entry.insert(0, "372") # A325
        self.fnv_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Capacity", command=self.calculate)
        self.calc_btn.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=8, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            db = float(self.db_entry.get())
            n = float(self.n_entry.get())
            fnv = float(self.fnv_entry.get())

            res = calculate_bolt_shear(db, n, fnv)
            
            self.last_inputs = {
                "Bolt Diameter": f"{db} mm",
                "Number of Bolts": n,
                "Shear Stress (Fnv)": f"{fnv} MPa"
            }
            self.last_results = {
                "One Bolt Area": f"{res['Ab']:.2f} mm2",
                "Nominal Strength": f"{res['Rn']/1000:.2f} kN",
                "Design Strength": f"{res['phi_Rn']/1000:.2f} kN",
                "status": "Calculated"
            }
            self.export_btn.configure(state="normal")

            output = f"Bolt Diameter: {db} mm\n"
            output += f"Number of Bolts: {n}\n"
            output += f"Nominal Shear Stress (Fnv): {fnv} MPa\n"
            output += "-"*30 + "\n"
            output += f"One Bolt Area (Ab): {res['Ab']:.2f} mm2\n"
            output += f"Nominal Strength (Rn): {res['Rn']/1000:.2f} kN\n"
            output += "-"*30 + "\n"
            output += f"DESIGN STRENGTH (Phi_Rn): {res['phi_Rn']/1000:.2f} kN\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class FlexureView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Flexural Member (Beam) Calculator", **kwargs)

        # Profile Selection
        self.profile_label = ctk.CTkLabel(self, text="Select Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Unbraced Length
        self.lb_label = ctk.CTkLabel(self, text="Unbraced Length, Lb (mm):")
        self.lb_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.lb_entry = ctk.CTkEntry(self, placeholder_text="3000")
        self.lb_entry.insert(0, "3000")
        self.lb_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Cb Factor
        self.cb_label = ctk.CTkLabel(self, text="Moment Gradient Factor, Cb:")
        self.cb_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.cb_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.cb_entry.insert(0, "1.0")
        self.cb_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Fy
        self.fy_label = ctk.CTkLabel(self, text="Yield Strength, Fy (MPa):")
        self.fy_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fy_entry = ctk.CTkEntry(self, placeholder_text="240")
        self.fy_entry.insert(0, "240")
        self.fy_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Capacity", command=self.calculate)
        self.calc_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=10, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            Lb = float(self.lb_entry.get())
            Cb = float(self.cb_entry.get())
            fy = float(self.fy_entry.get())

            from core.calculations import calculate_flexure
            res = calculate_flexure(profile, Lb, Cb, fy)

            self.last_inputs = {
                "Profile": profile_name,
                "Unbraced Length (Lb)": f"{Lb} mm",
                "Cb Factor": Cb,
                "Yield Strength (Fy)": f"{fy} MPa"
            }
            self.last_results = {
                "Plastic Moment (Mp)": f"{res['Mp']/1000000:.2f} kNm",
                "Nominal Moment (Mn)": f"{res['Mn']/1000000:.2f} kNm",
                "Design Strength": f"{res['phi_Mn']/1000000:.2f} kNm",
                "Limit State": res['state'],
                "status": "Calculated"
            }
            self.export_btn.configure(state="normal")

            output = f"Profile: {profile.name}\n"
            output += f"Lp: {res['Lp']:.0f} mm, Lr: {res['Lr']:.0f} mm\n"
            output += f"State: {res['state']}\n"
            output += "-"*30 + "\n"
            output += f"Plastic Moment (Mp): {res['Mp']/1000000:.2f} kNm\n"
            output += f"Nominal Moment (Mn): {res['Mn']/1000000:.2f} kNm\n"
            output += "-"*30 + "\n"
            output += f"DESIGN STRENGTH (Phi_Mn): {res['phi_Mn']/1000000:.2f} kNm\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class WeldView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Welded Connection Calculator", **kwargs)

        # Weld Type
        self.type_label = ctk.CTkLabel(self, text="Weld Type:")
        self.type_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.type_var = ctk.StringVar(value="Fillet")
        self.type_combo = ctk.CTkComboBox(self, values=["Fillet", "Groove"], variable=self.type_var)
        self.type_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Electrode
        self.elec_label = ctk.CTkLabel(self, text="Electrode Strength, Fexx (MPa):")
        self.elec_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.elec_entry = ctk.CTkEntry(self, placeholder_text="490")
        self.elec_entry.insert(0, "490") # E70xx
        self.elec_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Size
        self.size_label = ctk.CTkLabel(self, text="Size (Leg 'a' or Throat 'te') (mm):")
        self.size_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.size_entry = ctk.CTkEntry(self, placeholder_text="6")
        self.size_entry.insert(0, "6")
        self.size_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Length
        self.len_label = ctk.CTkLabel(self, text="Length of Weld (mm):")
        self.len_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.len_entry = ctk.CTkEntry(self, placeholder_text="100")
        self.len_entry.insert(0, "100")
        self.len_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Capacity", command=self.calculate)
        self.calc_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=10, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            weld_type = self.type_var.get()
            fexx = float(self.elec_entry.get())
            size = float(self.size_entry.get())
            length = float(self.len_entry.get())

            from core.calculations import calculate_weld
            res = calculate_weld(weld_type, fexx, size, length)

            self.last_inputs = {
                "Weld Type": weld_type,
                "Electrode (Fexx)": f"{fexx} MPa",
                "Size": f"{size} mm",
                "Length": f"{length} mm"
            }
            self.last_results = {
                "Effective Area": f"{res['Awe']:.2f} mm2",
                "Nominal Stress": f"{res['Fnw']:.2f} MPa",
                "Design Strength": f"{res['phi_Rn']/1000:.2f} kN",
                "status": "Calculated"
            }
            self.export_btn.configure(state="normal")

            output = f"Weld Type: {weld_type}\n"
            output += f"Electrode Fexx: {fexx} MPa\n"
            output += f"Size: {size} mm, Length: {length} mm\n"
            output += "-"*30 + "\n"
            output += f"Effective Throat (te): {(res['Awe']/length):.2f} mm\n"
            output += f"Effective Area (Awe): {res['Awe']:.2f} mm2\n"
            output += f"Nominal Stress (Fnw): {res['Fnw']:.2f} MPa\n"
            output += f"Nominal Strength (Rn): {res['Rn']/1000:.2f} kN\n"
            output += "-"*30 + "\n"
            output += f"DESIGN STRENGTH (Phi_Rn): {res['phi_Rn']/1000:.2f} kN\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class CombinedView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Beam-Column Capacity (Interaction)", **kwargs)

        # Profile Selection
        self.profile_label = ctk.CTkLabel(self, text="Select Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Loads
        self.pu_label = ctk.CTkLabel(self, text="Required Axial Strength, Pu (kN):")
        self.pu_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.pu_entry = ctk.CTkEntry(self, placeholder_text="100")
        self.pu_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.mux_label = ctk.CTkLabel(self, text="Required Moment X, Mux (kNm):")
        self.mux_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.mux_entry = ctk.CTkEntry(self, placeholder_text="50")
        self.mux_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.muy_label = ctk.CTkLabel(self, text="Required Moment Y, Muy (kNm):")
        self.muy_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.muy_entry = ctk.CTkEntry(self, placeholder_text="0")
        self.muy_entry.insert(0, "0")
        self.muy_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Geometry
        self.len_label = ctk.CTkLabel(self, text="Unbraced Length, L (mm):")
        self.len_label.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.len_entry = ctk.CTkEntry(self, placeholder_text="3000")
        self.len_entry.insert(0, "3000")
        self.len_entry.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Fy
        self.fy_label = ctk.CTkLabel(self, text="Yield Strength, Fy (MPa):")
        self.fy_label.grid(row=11, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fy_entry = ctk.CTkEntry(self, placeholder_text="240")
        self.fy_entry.insert(0, "240")
        self.fy_entry.grid(row=12, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Interaction Ratio", command=self.calculate)
        self.calc_btn.grid(row=13, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=150)
        self.result_text.grid(row=14, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            
            # Convert Inputs: kN -> N, kNm -> Nmm
            Pu = float(self.pu_entry.get()) * 1000
            Mux = float(self.mux_entry.get()) * 1000000
            Muy = float(self.muy_entry.get()) * 1000000
            
            L = float(self.len_entry.get())
            Fy = float(self.fy_entry.get())
            K = 1.0 # Default
            Cb = 1.0 # Default

            from core.calculations import calculate_combined
            res = calculate_combined(profile, Pu, Mux, Muy, L, K, Cb, Fy)

            self.last_inputs = {
                "Profile": profile_name,
                "Pu": f"{Pu/1000} kN",
                "Mux": f"{Mux/1000000} kNm",
                "Muy": f"{Muy/1000000} kNm",
                "Length": f"{L} mm"
            }
            self.last_results = {
                "Interaction Ratio": f"{res['ratio']:.3f}",
                "Axial Ratio": f"{res['Pr']:.3f}",
                "Flexural Ratio X": f"{res['Mrx']:.3f}",
                "Flexural Ratio Y": f"{res['Mry']:.3f}",
                "Equation": res['eq'],
                "status": res['status']
            }
            self.export_btn.configure(state="normal")

            output = f"Interaction Ratio: {res['ratio']:.3f}\n"
            output += f"Status: {res['status']}\n"
            output += f"Equation Used: {res['eq']}\n"
            output += "-"*30 + "\n"
            output += f"Axial Ratio (Pr): {res['Pr']:.3f}\n"
            output += f"Flexural Ratio X (Mrx): {res['Mrx']:.3f}\n"
            output += f"Flexural Ratio Y (Mry): {res['Mry']:.3f}\n"
            output += "-"*30 + "\n"
            output += f"Phi Pn: {res['phi_Pn']/1000:.2f} kN\n"
            output += f"Phi Mnx: {res['phi_Mnx']/1000000:.2f} kNm\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class SectionView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Profile Section Visualizer", **kwargs)
        
        # Hide Export Button for Visualizer
        self.export_btn.grid_forget()

        # Profile Selection
        self.profile_label = ctk.CTkLabel(self, text="Select Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var, command=self.update_plot)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Plot Frame
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(3, weight=1) # Allow plot to expand
        
        # Initial Plot
        self.canvas = None
        self.after(100, lambda: self.update_plot(self.profile_var.get()))

    def update_plot(self, profile_name):
        profile = self.db.get_profile(profile_name)
        
        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        from core.plotting import create_section_plot
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        fig = create_section_plot(profile)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

class BasePlateView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Column Base Plate Design", **kwargs)

        # Profile Selection (Column)
        self.profile_label = ctk.CTkLabel(self, text="Select Column Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Load
        self.pu_label = ctk.CTkLabel(self, text="Factored Axial Load, Pu (kN):")
        self.pu_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.pu_entry = ctk.CTkEntry(self, placeholder_text="500")
        self.pu_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Concrete
        self.fc_label = ctk.CTkLabel(self, text="Concrete Strength, fc' (MPa):")
        self.fc_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.fc_entry = ctk.CTkEntry(self, placeholder_text="25")
        self.fc_entry.insert(0, "25")
        self.fc_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Plate Dimensions
        self.n_label = ctk.CTkLabel(self, text="Plate Length, N (mm) [Parallel to Depth]:")
        self.n_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.n_entry = ctk.CTkEntry(self, placeholder_text="400")
        self.n_entry.insert(0, "400")
        self.n_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.b_label = ctk.CTkLabel(self, text="Plate Width, B (mm) [Perpendicular]:")
        self.b_label.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.b_entry = ctk.CTkEntry(self, placeholder_text="400")
        self.b_entry.insert(0, "400")
        self.b_entry.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Calculate Base Plate", command=self.calculate)
        self.calc_btn.grid(row=11, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=200)
        self.result_text.grid(row=20, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            
            Pu_kN = float(self.pu_entry.get())
            Pu = Pu_kN * 1000
            fc = float(self.fc_entry.get())
            N_plate = float(self.n_entry.get())
            B_plate = float(self.b_entry.get())

            from core.calculations import calculate_base_plate
            res = calculate_base_plate(Pu, fc, B_plate, N_plate, profile.d, profile.bf)

            self.last_inputs = {
                "Column Profile": profile_name,
                "Axial Load (Pu)": f"{Pu_kN} kN",
                "Concrete fc": f"{fc} MPa",
                "Plate Size": f"{N_plate}x{B_plate} mm"
            }
            self.last_results = {
                "Bearing Ratio": f"{res['bearing_ratio']:.3f}",
                "Required Thickness": f"{res['t_req']:.2f} mm",
                "Bearing Capacity": f"{res['phi_Pp']/1000:.2f} kN",
                "status": res['status']
            }
            self.export_btn.configure(state="normal")

            output = f"Base Plate Check for {profile_name}\n"
            output += f"Plate Size: {N_plate} x {B_plate} mm\n"
            output += "-"*30 + "\n"
            output += f"Concrete Bearing Capacity (Phi Pp): {res['phi_Pp']/1000:.2f} kN\n"
            output += f"Bearing Ratio: {res['bearing_ratio']:.3f}\n"
            output += f"Status: {res['status']}\n"
            output += "-"*30 + "\n"
            output += f"Cantilever m: {res['m']:.2f} mm\n"
            output += f"Cantilever n: {res['n']:.2f} mm\n"
            output += f"REQUIRED THICKNESS (tp): {res['t_req']:.2f} mm\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")

class MomentConnectionView(BaseView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "Moment End Plate Design", **kwargs)

        # Profile Selection (Beam)
        self.profile_label = ctk.CTkLabel(self, text="Select Beam Profile:")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_var = ctk.StringVar(value=self.profiles[0])
        self.profile_combo = ctk.CTkComboBox(self, values=self.profiles, variable=self.profile_var)
        self.profile_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Load
        self.mu_label = ctk.CTkLabel(self, text="Factored Moment, Mu (kNm):")
        self.mu_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.mu_entry = ctk.CTkEntry(self, placeholder_text="50")
        self.mu_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Bolt Details
        self.bolt_label = ctk.CTkLabel(self, text="Bolt Diameter (mm):")
        self.bolt_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.bolt_entry = ctk.CTkEntry(self, placeholder_text="16")
        self.bolt_entry.insert(0, "16")
        self.bolt_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.n_bolts_label = ctk.CTkLabel(self, text="Number of Tension Bolts:")
        self.n_bolts_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.n_bolts_entry = ctk.CTkEntry(self, placeholder_text="4")
        self.n_bolts_entry.insert(0, "4")
        self.n_bolts_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Plate Details
        self.tp_label = ctk.CTkLabel(self, text="End Plate Thickness (mm):")
        self.tp_label.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.tp_entry = ctk.CTkEntry(self, placeholder_text="20")
        self.tp_entry.insert(0, "20")
        self.tp_entry.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Calculate
        self.calc_btn = ctk.CTkButton(self, text="Check Connection", command=self.calculate)
        self.calc_btn.grid(row=11, column=0, padx=20, pady=20, sticky="ew")

        # Result
        self.result_text = ctk.CTkTextbox(self, height=200)
        self.result_text.grid(row=20, column=0, padx=20, pady=10, sticky="nsew")

    def calculate(self):
        try:
            profile_name = self.profile_var.get()
            profile = self.db.get_profile(profile_name)
            
            Mu = float(self.mu_entry.get())
            d_bolt = float(self.bolt_entry.get())
            n_bolts = int(self.n_bolts_entry.get())
            t_plate = float(self.tp_entry.get())

            from core.calculations import calculate_moment_plate
            res = calculate_moment_plate(Mu, d_bolt, n_bolts, t_plate, profile)

            self.last_inputs = {
                "Beam Profile": profile_name,
                "Moment (Mu)": f"{Mu} kNm",
                "Bolts": f"{n_bolts} x M{d_bolt}",
                "Plate Thickness": f"{t_plate} mm"
            }
            self.last_results = {
                "Bolt Tension": f"{res['Tu_bolt']/1000:.2f} kN",
                "Bolt Capacity": f"{res['phi_Rn_bolt']/1000:.2f} kN",
                "Ratio": f"{res['bolt_ratio']:.3f}",
                "Plate Check": res['plate_check'],
                "status": res['status']
            }
            self.export_btn.configure(state="normal")

            output = f"Moment End Plate Check for {profile_name}\n"
            output += "*"*30 + "\n"
            output += f"Applied Moment: {Mu} kNm\n"
            output += f"Total Tension Force: {res['Tu_total']/1000:.2f} kN\n"
            output += "-"*30 + "\n"
            output += f"Tension per Bolt: {res['Tu_bolt']/1000:.2f} kN\n"
            output += f"Bolt Capacity (Phi Rn): {res['phi_Rn_bolt']/1000:.2f} kN\n"
            output += f"Bolt Ratio: {res['bolt_ratio']:.3f}\n"
            output += "-"*30 + "\n"
            output += f"Plate Thickness Check: {res['plate_check']}\n"
            output += f"STATUS: {res['status']}\n"

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", output)
        except ValueError:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Error: Invalid input values.")
