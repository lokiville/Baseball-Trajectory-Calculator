import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
from math import sqrt, pi, exp, cos, sin, atan2

def hit_trajectory_calculator(x0, y0, z0, exit_speed, launch_angle, direction, sign):
    # Parameters
    mass = 5.125
    circ = 9.125
    wg = 0
    tau = 10000
    dt = 0.01
    temp_f = 70
    elev = 15
    vwind = 0
    phiwind = 0
    hwind = 0
    rh = 50
    bp_inhg = 29.92
    beta = 0.0001217
    flag = 1
    cd0 = 0.3008
    cdspin = 0.0292
    cl0 = 0.583
    cl1 = 2.333
    cl2 = 1.120

    # Derived constants
    temp_c = round((5 / 9) * (temp_f - 32), 1)
    elev_m = round(elev / 3.2808, 1)
    SVP = round(4.5841 * exp((18.687 - temp_c / 234.5) * temp_c / (257.14 + temp_c)), 1)
    bp_mmhg = round(bp_inhg * 1000 / 39.37, 1)
    rho_kgm = round(1.2929 * (273 / (temp_c + 273)) * (bp_mmhg * exp(-beta * elev_m) - 0.3783 * rh * SVP / 100) / 760, 3)
    rho_lbft = round(rho_kgm * 0.06261, 4)
    const = 0.07182 * rho_lbft * (5.125 / mass) * (circ / 9.125) ** 2

    # Initial spin calculations
    backspin = round(-763 + 120 * launch_angle + 21 * direction * sign)
    sidespin = round(-sign * 849 - 94 * direction)
    spin = round(sqrt(backspin ** 2 + sidespin ** 2))

    # Initial velocities
    v0 = round(exit_speed * 1.467, 1)
    v0x = round(v0 * cos(launch_angle * pi / 180) * sin(direction * pi / 180), 2)
    v0y = round(v0 * cos(launch_angle * pi / 180) * cos(direction * pi / 180), 2)
    v0z = round(v0 * sin(launch_angle * pi / 180), 2)

    # Initial angular velocities
    wx = round((-backspin * cos(direction * pi / 180) - sidespin * sin(launch_angle * pi / 180) * sin(direction * pi / 180) + wg * v0x / v0) * pi / 30, 1)
    wy = round((-backspin * sin(direction * pi / 180) - sidespin * sin(launch_angle * pi / 180) * cos(direction * pi / 180) + wg * v0y / v0) * pi / 30, 1)
    wz = round((sidespin * cos(launch_angle * pi / 180) + wg * v0z / v0) * pi / 30, 1)
    omega = round(sqrt(backspin ** 2 + sidespin ** 2) * pi / 30, 1)
    romega = round((circ / (2 * pi)) * omega / 12, 1)

    # 1st row calculations
    S = round((romega / v0) * exp(-0 / (tau * 146.7 / v0)), 4)
    Cd = round(cd0 + (cdspin * spin / 1000) * exp(-0 / (tau * 146.7 / v0)), 3)
    Cl = round(cl2 * S / (cl0 + cl1 * S), 4)
    romega_perp = round((spin * pi / 30) * (circ / (2 * pi)) / 12, 1)
    w_perp_w = round(romega_perp / romega, 3)

    vxw = vwind * 1.467 * sin(phiwind * pi / 180)
    vyw = vwind * 1.467 * cos(phiwind * pi / 180)

    adragx = round(-const * Cd * v0 * v0x, 3)
    adragy =  round(-const * Cd * v0 * v0y, 3)
    adragz = round(-const * Cd * v0 * v0z, 3)

    aMagx = const * (Cl / omega) * v0 * (wy * v0z - wz * (v0y - vyw)) / (w_perp_w)
    aMagy = - const * (Cl / omega) * v0 * (wz * (v0x - vxw) - wx * v0z) / (w_perp_w)
    aMagz = - const * (Cl / omega) * v0 * (wx * (v0y - vyw) - wy * (v0x - vxw)) / (w_perp_w)
    
    # DataFrame initialization
    columns = ["t", "x", "y", "z", "r", "phi", "vx", "vy", "vz", "v", "vmph", "w_perp", "romega_perp", "vw", "Cd", "S", "Cl", "vxw", "vyw", "adragx", "adragy", "adragz", "w_perp/w", "aMagx", "aMagy", "aMagz", "ax", "ay", "az", "flag"]
    df = pd.DataFrame(columns=columns)

    # First row calculations
    row = {
        "t": 0,
        "x": round(x0, 3),
        "y": round(y0, 3),
        "z": round(z0, 3),
        "r": round(sqrt(x0 ** 2 + y0 ** 2), 1),
        "phi": round(atan2(x0, y0) * 180 / pi, 1),
        "vx": round(v0x, 2),
        "vy": round(v0y, 2),
        "vz": round(v0z, 2),
        "v": round(sqrt(v0x ** 2 + v0y ** 2 + v0z ** 2), 1),
        "vmph": round(v0 / 1.467, 1),
        "w_perp": int(round(sqrt(spin ** 2 - flag * ((30 / pi) * (wx * v0x + wy * v0y + wz * v0z) / v0) ** 2))),
        "romega_perp": romega_perp,
        "vw": round(sqrt((v0x - vxw) ** 2 + (v0y - vyw) ** 2 + v0z ** 2), 1),
        "Cd": Cd,
        "S": S,
        "Cl": Cl,
        "vxw": round(0, 4),
        "vyw": round(0, 4),
        "adragx": round(-const * Cd * v0 * v0x, 3),
        "adragy": round(-const * Cd * v0 * v0y, 3),
        "adragz": round(-const * Cd * v0 * v0z, 3),
        "w_perp/w": w_perp_w,
        "aMagx": aMagx,
        "aMagy": aMagy,
        "aMagz": aMagz,
        "ax": round(adragx + aMagx, 3),
        "ay": round(adragy + aMagy, 3),
        "az": round(adragz + aMagz - 32.174, 3),
        "flag": 0,
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Iterative calculations
    while True:
        prev = df.iloc[-1]

        t = prev["t"] + dt
        vxw = vxw if t >= hwind else 0
        vyw = vyw if t >= hwind else 0

        ax = prev["adragx"] + prev["aMagx"]
        ay = prev["adragy"] + prev["aMagy"]
        az = prev["adragz"] + prev["aMagz"] - 32.174

        vx = prev["vx"] + ax * dt
        vy = prev["vy"] + ay * dt
        vz = prev["vz"] + az * dt

        x = prev["x"] + prev["vx"] * dt + 0.5 * prev["ax"] * dt ** 2
        y = prev["y"] + prev["vy"] * dt + 0.5 * prev["ay"] * dt ** 2
        z = prev["z"] + prev["vz"] * dt + 0.5 * prev["az"] * dt ** 2

        r = sqrt(x ** 2 + y ** 2)
        phi = atan2(x, y) * 180 / pi

        v = sqrt(vx ** 2 + vy ** 2 + vz ** 2)
        vmph = v / 1.467

        vw = sqrt((vx - vxw) ** 2 + (vy - vyw) ** 2 + vz ** 2)

        Cd = cd0 + (cdspin * prev["w_perp"] / 1000) * exp(-t / (tau * 146.7 / vw))
        S = (prev["romega_perp"] / vw) * exp(-t / (tau * 146.7 / vw))
        Cl = cl2 * S / (cl0 + cl1 * S)

        adragx = -const * Cd * vw * (vx - vxw)
        adragy = -const * Cd * vw * (vy - vyw)
        adragz = -const * Cd * vw * vz

        w_perp = sqrt(spin ** 2 - flag * ((30 / pi) * (wx * vx + wy * vy + wz * vz) / v) ** 2)
        romega_perp = (w_perp * pi / 30) * (circ / (2 * pi)) / 12

        w_perp_w = round(romega_perp / romega, 3)

        aMagx = const * (Cl / omega) * vw * (wy * vz - wz * (vy - vyw)) / (w_perp_w)
        aMagy = -const * (Cl / omega) * vw * (wz * (vx - vxw) - wx * vz) / (w_perp_w)
        aMagz = -const * (Cl / omega) * vw * (wx * (vy - vyw) - wy * (vx - vxw)) / (w_perp_w)

        ax = adragx + aMagx
        ay = adragy + aMagy
        az = adragz + aMagz - 32.174

        flag = 1 if (prev["z"] - z0) * (z - z0) < 0 else 0

        new_row = {
            "t": round(t, 2),
            "x": round(x, 3),
            "y": round(y, 3),
            "z": round(z, 3),
            "r": round(r, 1),
            "phi": round(phi, 1),
            "vx": round(vx, 2),
            "vy": round(vy, 2),
            "vz": round(vz, 2),
            "v": round(v, 1),
            "vmph": round(vmph, 1),
            "w_perp": int(round(w_perp)),
            "romega_perp": round(romega_perp, 1),
            "vw": round(vw, 1),
            "Cd": round(Cd, 3),
            "S": round(S, 4),
            "Cl": round(Cl, 4),
            "vxw": round(vxw, 4),
            "vyw": round(vyw, 4),
            "adragx": round(adragx, 3),
            "adragy": round(adragy, 3),
            "adragz": round(adragz, 3),
            "w_perp/w": round(w_perp / omega, 3),
            "aMagx": round(aMagx, 3),
            "aMagy": round(aMagy, 3),
            "aMagz": round(aMagz, 3),
            "ax": round(ax, 3),
            "ay": round(ay, 3),
            "az": round(az, 3),
            "flag": flag,
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        if flag == 1:
            break

    return df, df.loc[df['flag'] == 1, 'r'].iloc[0]
