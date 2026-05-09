import math


def calculate_fuselage_structure(radius_m, length_m, bending_moment_mnm,
                                  F_B=0.96, A_bar=138, frame_spacing_m=0.5,
                                  delta_P=75000, sigma_p_mpa=100):
    """
    Preliminary structural sizing of a fuselage.

    Parameters
    ----------
    radius_m            : float  Fuselage radius (m)
    length_m            : float  Fuselage length (m)
    bending_moment_mnm  : float  Design bending moment (MN·m)
    F_B                 : float  Buckling efficiency factor (default 0.96, built-up Z-stringer)
    A_bar               : float  Buckling/compression material constant (default 138, conv. alloy)
    frame_spacing_m     : float  Ring frame longitudinal pitch (m)
    delta_P             : float  Cabin differential pressure (Pa)
    sigma_p_mpa         : float  Allowable skin stress under pressure (MPa)

    Returns
    -------
    dict with all key sizing outputs
    """

    # ── Geometry ─────────────────────────────────────────────────────────────
    area_m2        = math.pi * radius_m ** 2          # cross-sectional area (m²)
    circumference_m = 2 * math.pi * radius_m          # fuselage circumference (m)

    # ── Step 1: Skin thickness to resist internal pressure (hoop stress) ─────
    # t_p = ΔP · R / σ_p
    t_p_mm = (delta_P * radius_m) / (sigma_p_mpa * 1e6) * 1e3

    # ── Step 2: Bending stress ────────────────────────────────────────────────
    # σ_a = F_B · Ā · √( M / (A · L) )
    M_Nm       = bending_moment_mnm * 1e6             # convert MN·m → N·m
    sigma_a_mpa = F_B * A_bar * math.sqrt(M_Nm / (area_m2 * frame_spacing_m * 1e6))

    # ── Step 3: Effective skin thickness for bending ──────────────────────────
    # t_e = M / (σ_a · A)
    t_e_m  = M_Nm / (sigma_a_mpa * 1e6 * area_m2)
    t_e_mm = t_e_m * 1e3

    # Governing skin thickness (pressure vs bending)
    t_skin_mm = max(t_p_mm, t_e_mm)
    governs   = "bending" if t_e_mm >= t_p_mm else "pressure"

    # ── Step 4: Stringer sizing ───────────────────────────────────────────────
    t_b_mm   = 0.65 * t_e_mm                         # stringer (base) thickness
    h_s_mm   = 40.0 * t_b_mm                         # stringer height
    f_w_mm   = 0.4  * h_s_mm                         # flange width
    A_str_mm2 = 72.0 * t_b_mm ** 2                   # single stringer area (Z-profile)

    # Skin area contribution → fraction assigned to stringers
    A_b_mm2     = t_e_mm * circumference_m * 1e3     # total effective skin area (mm²)
    A_b_str_mm2 = A_b_mm2 * 0.35                     # 35 % for stringers
    n_stringers  = round(A_b_str_mm2 / A_str_mm2)

    # ── Step 5: Ring frame count ──────────────────────────────────────────────
    n_frames     = math.floor(length_m / frame_spacing_m)

    # ── Step 6: Ring frame web height (3 % of fuselage diameter) ─────────────
    web_height_mm = 0.03 * (2 * radius_m) * 1e3

    return {
        "Fuselage radius (m)"              : round(radius_m, 3),
        "Fuselage length (m)"              : round(length_m, 2),
        "Cross-sectional area (m²)"        : round(area_m2, 4),
        "Circumference (m)"                : round(circumference_m, 4),
        "Skin thickness – pressure (mm)"   : round(t_p_mm, 3),
        "Effective skin thickness – bending (mm)": round(t_e_mm, 3),
        "Governing skin thickness (mm)"    : round(t_skin_mm, 3),
        "Governing load case"              : governs,
        "Bending stress σ_a (MPa)"         : round(sigma_a_mpa, 2),
        "Stringer thickness t_b (mm)"      : round(t_b_mm, 3),
        "Stringer height h_s (mm)"         : round(h_s_mm, 2),
        "Flange width f_w (mm)"            : round(f_w_mm, 3),
        "Stringer area A_str (mm²)"        : round(A_str_mm2, 2),
        "No. of stringers"                 : n_stringers,
        "No. of ring frames"               : n_frames,
        "Ring frame web height (mm)"       : round(web_height_mm, 1),
    }


# ── Example run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = calculate_fuselage_structure(
        radius_m           = 1.675,
        length_m           = 38.4,
        bending_moment_mnm = 3.0,
    )

    print("\n── Fuselage Preliminary Sizing ──────────────────────────")
    for key, value in results.items():
        print(f"  {key:<45} {value}")
    print("─────────────────────────────────────────────────────────\n")
