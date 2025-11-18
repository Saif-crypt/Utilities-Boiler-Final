# Inside your existing code, only replace the image HTML and CSS parts for each KPI card as below:

# ---------- CSS (Update ONLY .kpi-topbox img selector) ----------
st.markdown(
    """
    <style>
      .kpi-topbox img {
        width:100%;
        height:100%;
        object-fit:contain;
        display:block;
        margin:0 auto;
        box-sizing:border-box;
        background:transparent;
      }
      /* ... rest of your CSS remains untouched ... */
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- KPI cards (icons in top boxes + sparkline under values) ----------
kpi_cols = st.columns(4, gap="large")

# KPI 1: Efficiency
with kpi_cols[0]:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    b = make_icon("flame", w=360, h=72)
    b64 = bytes_to_base64_str(b)
    # Inline style for perfect fit
    st.markdown(f"<div class='kpi-topbox'><img src='data:image/png;base64,{b64}' alt='flame' style='width:100%;height:100%;object-fit:contain;'/></div>", unsafe_allow_html=True)
    avg_eff = filtered_df["Efficiency_X"].mean()
    prev_avg = (
        df.loc[df["Date"] < filtered_df["Date"].min(), "Efficiency_X"].mean()
        if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
        else avg_eff
    )
    delta = avg_eff - (prev_avg if not np.isnan(prev_avg) else avg_eff)
    st.markdown("<div class='kpi-title'>Average Efficiency</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{avg_eff:.1f}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-delta'>{delta:+.2f}% vs prev</div>", unsafe_allow_html=True)
    sp = sparkline_png(filtered_df["Efficiency_X"], width_px=360, height_px=48, line_color="#8fd3ff")
    st.markdown("<div class='kpi-spark'>", unsafe_allow_html=True)
    st.image(sp, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 2: Total Fuel
with kpi_cols[1]:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    b = make_icon("fuel", w=360, h=72)
    b64 = bytes_to_base64_str(b)
    st.markdown(f"<div class='kpi-topbox'><img src='data:image/png;base64,{b64}' alt='fuel' style='width:100%;height:100%;object-fit:contain;'/></div>", unsafe_allow_html=True)
    total_fuel = filtered_df["Total_Fuel_Corrected"].sum()
    prev_fuel = (
        df.loc[df["Date"] < filtered_df["Date"].min(), "Total_Fuel_Corrected"].sum()
        if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
        else total_fuel
    )
    delta_fuel = total_fuel - prev_fuel
    st.markdown("<div class='kpi-title'>Total Fuel</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{total_fuel:.0f} units</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-delta'>{delta_fuel:+.0f} units vs prev</div>", unsafe_allow_html=True)
    sp = sparkline_png(filtered_df["Total_Fuel_Corrected"], width_px=360, height_px=48, line_color="#9fe2a6")
    st.markdown("<div class='kpi-spark'>", unsafe_allow_html=True)
    st.image(sp, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 3: Avg Temp
with kpi_cols[2]:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    b = make_icon("therm", w=360, h=72)
    b64 = bytes_to_base64_str(b)
    st.markdown(f"<div class='kpi-topbox'><img src='data:image/png;base64,{b64}' alt='therm' style='width:100%;height:100%;object-fit:contain;'/></div>", unsafe_allow_html=True)
    avg_temp = filtered_df["Temperature"].mean()
    st.markdown("<div class='kpi-title'>Avg Temp</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{avg_temp:.1f}°C</div>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-sublabel'>Operational average</div>", unsafe_allow_html=True)
    sp = sparkline_png(filtered_df["Temperature"], width_px=360, height_px=48, line_color="#ffd28f")
    st.markdown("<div class='kpi-spark'>", unsafe_allow_html=True)
    st.image(sp, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 4: Avg Pressure
with kpi_cols[3]:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    b = make_icon("gauge", w=360, h=72)
    b64 = bytes_to_base64_str(b)
    st.markdown(f"<div class='kpi-topbox'><img src='data:image/png;base64,{b64}' alt='gauge' style='width:100%;height:100%;object-fit:contain;'/></div>", unsafe_allow_html=True)
    avg_pres = filtered_df["Pressure"].mean()
    st.markdown("<div class='kpi-title'>Avg Pressure</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{avg_pres:.1f} kPa</div>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-sublabel'>Mean operating pressure</div>", unsafe_allow_html=True)
    sp = sparkline_png(filtered_df["Pressure"], width_px=360, height_px=48, line_color="#9bd1ff")
    st.markdown("<div class='kpi-spark'>", unsafe_allow_html=True)
    st.image(sp, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
