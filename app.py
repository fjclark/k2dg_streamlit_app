"""Streamlit app to interconvert free energies and dissociation constants."""

from k2dg._parse import _parse_temperature, _parse_dg_units, _parse_k_units
from k2dg._print import _get_dg0_str, _get_kd0_str
from k2dg.conversion import dg0_to_kd0, kd0_to_dg0
import matplotlib.pyplot as plt
import streamlit as st

TO_DG_STR = "$K_{\mathrm{D}}$ to $\Delta G^o_{\mathrm{Bind}}$"
TO_KD_STR = "$\Delta G^o_{\mathrm{Bind}}$ to $K_{\mathrm{D}}$"
DG_STR = "$\Delta G^o_{\mathrm{Bind}}$"
KD_STR = "$K_{\mathrm{D}}$"


def main():
    # Title
    st.title("K2DG: Interconvert free energies and dissociation constants")

    # Select free energy to dissociation constant or vice versa
    conversion = st.radio(
        label="Conversion",
        options=(TO_DG_STR, TO_KD_STR),
    )

    # Temperature required in both cases
    temperature_input = st.number_input("Temperature (K)", value=298.15, step=10.0)
    temperature = _parse_temperature(temperature_input)

    # Free energy to dissociation constant
    if conversion == TO_KD_STR:
        # Input
        left, right = st.columns(2)
        with left:
            free_energy_input = st.number_input(
                DG_STR, value=0.0, step=1.0, max_value=0.0
            )
        with right:
            free_energy_units = st.selectbox("Units", options=("kcal/mol", "kJ/mol"))

        # Convert into required units
        free_energy_units = _parse_dg_units(free_energy_units)
        free_energy = free_energy_input * free_energy_units

        # Calculate dissociation constant
        dissociation_constant = dg0_to_kd0(dg0=free_energy, temperature=temperature)

        # Output dissociation constant in big green box
        kd0_str = _get_kd0_str(kd0=dissociation_constant)
        st.success(f"Dissociation constant = {kd0_str}")

    if conversion == TO_DG_STR:
        # Input temperature and dissociation constant in side-by-side drop-down boxes
        left, right = st.columns(2)
        with left:
            dissociation_constant_input = st.number_input(
                KD_STR, value=1.0, step=1.0, min_value=1e-12
            )
        with right:
            dissociation_constant_units = st.selectbox(
                "Units", options=("nM", "uM", "mM", "M")
            )

        # Convert into required units
        dissociation_constant_units = _parse_k_units(dissociation_constant_units)
        dissociation_constant = (
            dissociation_constant_input * dissociation_constant_units
        )

        # Calculate free energy
        free_energy = kd0_to_dg0(kd0=dissociation_constant, temperature=temperature)

        # Output free energy
        dg0_str = _get_dg0_str(dg0=free_energy)
        st.success(f"Free energy of binding = {dg0_str}")

    # Create a plot of the free energy to dissociation constant relationship at the supplied temperature
    # Create a range of dissociation constants
    kd_range = [1e-20 * 10 ** (i / 10) for i in range(200)]
    dg0_range = [
        kd0_to_dg0(kd0=kd, temperature=temperature).to("kcal/mol").magnitude
        for kd in kd_range
    ]

    # Create a plot
    fig, ax = plt.subplots()
    ax.plot(kd_range, dg0_range)
    # Add current value to plot
    ax.scatter(dissociation_constant, free_energy.to("kcal/mol").magnitude, color="red")
    ax.set_xscale("log")
    # Set limits based on kd of 10-12 to 10-2
    xlims = (1e-12, 1e-1)
    ylims = [
        kd0_to_dg0(kd0=xlim, temperature=temperature).to("kcal/mol").magnitude
        for xlim in xlims
    ]
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.set_xlabel(f"{KD_STR} (M)")
    ax.set_ylabel(f"{DG_STR} (kcal/mol)")
    ax.set_title(f"{KD_STR} vs {DG_STR} at {temperature}")
    st.pyplot(fig)


if __name__ == "__main__":
    main()
