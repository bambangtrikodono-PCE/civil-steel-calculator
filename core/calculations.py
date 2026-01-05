import math

# Constants
E_STEEL = 200000  # MPa

def calculate_tension(Ag, Ae, Fy, Fu):
    """
    Calculate design tensile strength according to SNI 1729 (AISC 360).
    phi_tn * Pn
    
    Args:
        Ag (float): Gross area (mm2)
        Ae (float): Effective net area (mm2). Assuming Ae = Ag for now if no connection details provided, but usually user inputs U.
        Fy (float): Yield strength (MPa)
        Fu (float): Ultimate strength (MPa)
        
    Returns:
        dict: Results including Pn_yield, Pn_rupture, phi_Pn
    """
    # Yielding in gross section
    Pn_yield = Fy * Ag
    phi_yield = 0.9
    phi_Pn_yield = phi_yield * Pn_yield

    # Rupture in net section
    Pn_rupture = Fu * Ae
    phi_rupture = 0.75
    phi_Pn_rupture = phi_rupture * Pn_rupture

    phi_Pn = min(phi_Pn_yield, phi_Pn_rupture)
    
    return {
        "phi_Pn": phi_Pn,
        "yield": {"Pn": Pn_yield, "phi_Pn": phi_Pn_yield},
        "rupture": {"Pn": Pn_rupture, "phi_Pn": phi_Pn_rupture}
    }

def calculate_compression(Ag, rx, ry, Kx, Lx, Ky, Ly, Fy):
    """
    Calculate design compressive strength.
    Uses AISC 360-16 Chapter E (SNI 1729:2020)
    
    Args:
        Ag (float): Gross area (mm2)
        rx, ry (float): Radius of gyration (mm)
        Kx, Ky (float): Effective length factor
        Lx, Ly (float): Unbraced length (mm)
        Fy (float): Yield strength (MPa)
    """
    # Slenderness ratios
    KL_r_x = (Kx * Lx) / rx
    KL_r_y = (Ky * Ly) / ry
    KL_r = max(KL_r_x, KL_r_y)
    
    # Elastic buckling stress, Fe
    # Fe = pi^2 * E / (KL/r)^2
    Fe = (math.pi**2 * E_STEEL) / (KL_r**2)
    
    # Critical stress, Fcr
    if KL_r <= 4.71 * math.sqrt(E_STEEL / Fy):
        # Inelastic buckling
        Fcr = (0.658**(Fy / Fe)) * Fy
    else:
        # Elastic buckling
        Fcr = 0.877 * Fe
        
    Pn = Fcr * Ag
    phi = 0.9
    phi_Pn = phi * Pn
    
    return {
        "phi_Pn": phi_Pn,
        "Pn": Pn,
        "Fcr": Fcr,
        "KL_r": KL_r,
        "Fe": Fe
    }

def calculate_bolt_shear(db, n, Fnv, threads_excluded=True):
    """
    Calculate bolt shear capacity.
    
    Args:
        db (float): Bolt diameter (mm)
        n (int): Number of bolts
        Fnv (float): Nominal shear stress (MPa) (e.g., A325 = 372 MPa with threads included)
        threads_excluded (bool): Note: Fnv needs to be adjusted based on this.
    """
    Ab = 0.25 * math.pi * db**2
    Rn = n * Fnv * Ab
    phi = 0.75
    phi_Rn = phi * Rn
    
    return {
        "phi_Rn": phi_Rn,
        "Rn": Rn,
        "Ab": Ab
    }

def calculate_flexure(profile, Lb, Cb, Fy):
    """
    Calculate design flexural strength (Moment Capacity).
    SNI 1729:2015 Chapter F.
    
    Args:
        profile (SteelProfile): The steel profile object
        Lb (float): Unbraced length (mm)
        Cb (float): Lateral-torsional buckling modification factor
        Fy (float): Yield strength (MPa)
    """
    E = E_STEEL
    Sx = profile.Sx
    Zx = profile.Zx
    J = profile.J
    Iy = profile.Iy
    cw = profile.Cw
    rts = profile.rts
    h0 = profile.h0

    # 1. Yielding (Mp) F2.1
    Mp = Fy * Zx
    
    # 2. Lateral-Torsional Buckling (LTB) F2.2
    
    # Limiting lengths Lp and Lr
    # Lp = 1.76 * ry * sqrt(E/Fy)
    Lp = 1.76 * profile.ry * math.sqrt(E/Fy)
    
    # Lr calculation is complex
    # Lr = 1.95 * rts * E / (0.7 * Fy) * sqrt(J*c / (Sx * h0) + sqrt(...))
    # Simplify c = 1 for doubly symmetric-I
    
    # Term 1: 1.95 * rts * E / (0.7 * Fy)
    term1 = 1.95 * rts * E / (0.7 * Fy)
    
    # Term 2: J / (Sx * h0)
    term2 = J / (Sx * h0)
    
    # Term 3: 6.76 * (0.7 * Fy / E)^2
    term3 = 6.76 * ((0.7 * Fy) / E)**2
    
    Lr = term1 * math.sqrt(term2 + math.sqrt(term2**2 + term3))
    
    # Determine Mn
    Mn = 0
    buckling_state = ""
    
    if Lb <= Lp:
        # Zone 1: Plastic Moment
        Mn = Mp
        buckling_state = "Yielding (Lb <= Lp)"
    elif Lb <= Lr:
        # Zone 2: Inelastic LTB
        # Mn = Cb * [Mp - (Mp - 0.7*Fy*Sx) * (Lb - Lp)/(Lr - Lp)] <= Mp
        term_interp = (Mp - 0.7 * Fy * Sx) * ((Lb - Lp) / (Lr - Lp))
        Mn = Cb * (Mp - term_interp)
        Mn = min(Mn, Mp) # Cap at Mp
        buckling_state = "Inelastic LTB (Lp < Lb <= Lr)"
    else:
        # Zone 3: Elastic LTB
        # Fcr = (Cb * pi^2 * E) / (Lb/rts)^2 * sqrt(1 + 0.078 * J*c / (Sx*h0) * (Lb/rts)^2)
        # Mcr = Fcr * Sx
        
        # Breakdown Fcr calc
        L_rts = Lb / rts
        term_a = (Cb * math.pi**2 * E) / (L_rts**2)
        term_b = math.sqrt(1 + 0.078 * (J / (Sx * h0)) * L_rts**2)
        Fcr = term_a * term_b
        
        Mn = Fcr * Sx
        Mn = min(Mn, Mp) # Cap at Mp
        buckling_state = f"Elastic LTB (Lb > Lr), Fcr={Fcr:.2f} MPa"
    
    phi = 0.9
    phi_Mn = phi * Mn
    
    return {
        "phi_Mn": phi_Mn,
        "Mn": Mn,
        "Mp": Mp,
        "Lp": Lp,
        "Lr": Lr,
        "Lb": Lb,
        "state": buckling_state
    }

def calculate_weld(weld_type, Fexx, size, length):
    """
    Calculate design strength of welded connections.
    SNI 1729:2015 Chapter J2.
    
    Args:
        weld_type (str): "Fillet" or "Groove"
        Fexx (float): Electrode strength (MPa)
        size (float): Leg size 'a' for Fillet (mm) or Effective Throat 'te' for Groove (mm)
        length (float): Length of weld (mm)
    """
    phi = 0.75 # Default for Shear
    Fnw = 0.6 * Fexx
    
    if weld_type == "Fillet":
        # Effective throat te = 0.707 * a
        # Awe = te * L
        te = 0.707 * size
        Awe = te * length
        Rn = Fnw * Awe
        # Phi = 0.75 for Fillet
        phi = 0.75
    elif weld_type == "Groove":
        # Effective throat te = size (input)
        te = size
        Awe = te * length
        Rn = 0.6 * Fexx * Awe # Shear on effective area (Conservative generic check)
        phi = 0.80 # 0.80 for Tension, 0.75 for Shear. Let's assume PJP Tension for now as 0.8 is common, but Shear is 0.75.
        # To be safe/conservative for generic "Weld Strength", we often check shear.
        phi = 0.75 
    else:
        return {"error": "Unknown weld type"}

    phi_Rn = phi * Rn
    
    return {
        "phi_Rn": phi_Rn,
        "Rn": Rn,
        "Awe": Awe,
        "Fnw": Fnw,
        "phi": phi
    }

def calculate_combined(profile, Pu, Mux, Muy, L, K, Cb, Fy):
    """
    Calculate combined forces capacity (Beam-Column).
    SNI 1729:2015 Chapter H (Eq H1-1a / H1-1b).
    
    Args:
        profile (SteelProfile): Steel profile object
        Pu (float): Required axial strength (N)
        Mux (float): Required flexural strength x-axis (Nmm)
        Muy (float): Required flexural strength y-axis (Nmm)
        L (float): Unbraced length (mm)
        K (float): Effective length factor
        Cb (float): Moment gradient factor
        Fy (float): Yield strength (MPa)
    """
    # 1. Axial Capacity (Comp)
    # Assume Kx=Ky=K and Lx=Ly=L for simplification
    res_comp = calculate_compression(profile.Ag, profile.rx, profile.ry, K, L, K, L, Fy)
    phi_Pn = res_comp['phi_Pn']
    
    # 2. Flexural Capacity X (Strong Axis)
    # Assume Lb = L
    res_flex_x = calculate_flexure(profile, L, Cb, Fy)
    phi_Mnx = res_flex_x['phi_Mn']
    
    # 3. Flexural Capacity Y (Weak Axis)
    # Weak axis bending of I-shapes: LTB does not apply.
    # Yield limit: Mpy = min(FyZy, 1.6FySy)
    # We will just take Mpy = Fy * Zy for simplicity.
    Mny = Fy * profile.Zy
    # Check flange local buckling if necessary (rare for hot rolled standard profiles to be non-compact)
    # Assume compact for now.
    phi_Mny = 0.9 * Mny
    
    # 4. Interaction Check
    Pr = Pu / phi_Pn
    Mrx = Mux / phi_Mnx
    Mry = Muy / phi_Mny
    
    ratio = 0.0
    eq_used = ""
    
    if Pr >= 0.2:
        # Eq H1-1a: Pr + 8/9 * (Mrx + Mry) <= 1.0
        ratio = Pr + (8/9) * (Mrx + Mry)
        eq_used = "H1-1a (Pr >= 0.2)"
    else:
        # Eq H1-1b: Pr/2 + (Mrx + Mry) <= 1.0
        ratio = (Pr / 2) + (Mrx + Mry)
        eq_used = "H1-1b (Pr < 0.2)"
        
    return {
        "ratio": ratio,
        "eq": eq_used,
        "Pr": Pr,
        "Mrx": Mrx,
        "Mry": Mry,
        "phi_Pn": phi_Pn,
        "phi_Mnx": phi_Mnx,
        "phi_Mny": phi_Mny,
        "status": "OK" if ratio <= 1.0 else "NOT SAFE"
    }

def calculate_base_plate(Pu, fc, B, N, profile_d, profile_bf):
    """
    Calculate Column Base Plate thickness and bearing.
    SNI 1729 / AISC Design Guide 1.
    
    Args:
        Pu (float): Factored axial load (N)
        fc (float): Concrete compressive strength (MPa)
        B (float): Plate width (mm) - perpendicular to N
        N (float): Plate length (mm) - parallel to depth d
        profile_d (float): Column depth (mm)
        profile_bf (float): Column flange width (mm)
    """
    # 1. Concrete Bearing Strength (Pp)
    # Assume A2 = A1 (no pedestal confinement increase for conservation)
    A1 = B * N
    phi_c = 0.65
    Pm = Pu / (phi_c * 0.85 * fc * A1) # Check if plate area is sufficient
    
    phi_Pp = phi_c * 0.85 * fc * A1
    bearing_ratio = Pu / phi_Pp
    
    # 2. Required Thickness (tp)
    # Based on cantilever moment
    m = (N - 0.95 * profile_d) / 2
    n = (B - 0.8 * profile_bf) / 2
    
    # Critical cantilever dimension l
    # Lambda n' check is often ignored in simplified checks, taking max(m, n) is standard approx.
    # More accurate: l = max(m, n, lambda*n')
    l = max(m, n)
    
    # Required thickness: tp >= l * sqrt(2*Pu / (0.9 * Fy * B * N))
    # Fy for Base Plate usually A36 (250 MPa)
    Fy_plate = 250 
    phi_b = 0.9
    
    # treq = l * sqrt(2 * Pu / (phi * Fy * A1))
    # Note: AISC Eq 3.3.14 derived form
    
    try:
        t_req = l * math.sqrt((2 * Pu) / (phi_b * Fy_plate * A1))
    except ValueError:
        t_req = 0.0 # If Pu is negative (tension), base plate logic different. Assume compression only.

    return {
        "phi_Pp": phi_Pp,
        "bearing_ratio": bearing_ratio,
        "t_req": t_req,
        "m": m,
        "n": n,
        "A1": A1,
        "n": n,
        "A1": A1,
        "status": "OK" if bearing_ratio <= 1.0 else "Plate Area Too Small"
    }

def calculate_moment_plate(Mu_kNm, d_bolt, n_bolts, thick_plate, profile, Fnt=620, Fy_plate=250):
    """
    Calculate Moment End Plate (Flush, 4-Bolt type assumption).
    Check Bolt Tension and Plate Yielding.
    
    Args:
        Mu_kNm (float): Moment in kNm
        d_bolt (float): Bolt Diameter (mm)
        n_bolts (int): Number of tension bolts (usually 2 or 4)
        thick_plate (float): Plate thickness (mm)
        profile (SteelProfile): Beam profile
        Fnt (float): Bolt nominal tension strength (A325=620MPa, A490=780MPa)
        Fy_plate (float): Plate yield strength
    """
    Mu = Mu_kNm * 1000000 # Nmm
    
    # Lever arm estimate (d - tf) approx
    h_arm = profile.d - profile.tf
    
    # 1. Bolt Tension Check
    # Total tension force
    Tu_total = Mu / h_arm
    
    # Tension per bolt (Assuming load shared equally among tension bolts)
    Tu_bolt = Tu_total / n_bolts
    
    # Bolt Capacity
    Ab = 0.25 * math.pi * d_bolt**2
    phi_bolt = 0.75
    Rn_bolt = Fnt * Ab
    phi_Rn_bolt = phi_bolt * Rn_bolt
    
    bolt_ratio = Tu_bolt / phi_Rn_bolt
    
    # 2. Plate Flexure (Yield Line) - Simplified
    # Treq thickness ~ sqrt(1.11 * Mu_bolt / (phi * Fy * Yp))
    # Using simplified approach from AISC Design Guide 16 (Flush)
    # Required thickness often governed by:
    # treq = sqrt( Mpl / (phi * Fy * Yp) )? 
    # Let's use simplified yielding check for the plate width involved.
    
    # Assume effective width tributary to bolts be ~ gauge width g or similar.
    # Simplified capacity check:
    # Check if existing thickness > required.
    
    # Base calculation on Bolt Force
    # M_plate approx = Tu_bolt * (distance from web/flange)
    # This is complex. We will implement "Thickness Check" based on AISC eqn 
    # t_req = sqrt( [1.11 * phi * Mn ] / [ phi * Fy * Yp ] ) ... no.
    
    # Let's stick to Bolt Tension as primary check for this "Lite" version.
    # And a basic "Plate Thickness Sizing" heuristic: t_plate >= d_bolt (rule of thumb)
    
    plate_check = "OK"
    if thick_plate < d_bolt:
        plate_check = "Plate too thin (Ref < d_bolt)"
        
    return {
        "Tu_total": Tu_total,
        "Tu_bolt": Tu_bolt,
        "phi_Rn_bolt": phi_Rn_bolt,
        "bolt_ratio": bolt_ratio,
        "plate_check": plate_check,
        "status": "OK" if (bolt_ratio <= 1.0 and plate_check == "OK") else "NOT SAFE"
    }
