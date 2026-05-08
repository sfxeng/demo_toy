


import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Time-to-Failure Demo",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Time to Failure – Two Random Sample Populations Demo")
st.markdown("""
**Demonstration**: Two random sample populations of **time-to-failure** events  
(e.g., component lifetime, machine reliability, reliability engineering).  

- **Group A**: Weibull distribution (realistic wear-out / increasing failure rate)  
- **Group B**: Exponential distribution (constant failure rate – memoryless)  

Click the button below to generate **completely new** random samples and watch the plots update instantly.
""")

# ──────────────────────────────────────────────
# Sidebar controls
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("Simulation Parameters")
    n = st.slider(
        "Sample size per group",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
        help="Larger samples = more stable statistics"
    )
    st.caption("🔄 New random samples are generated **only** when you click the button")

# ──────────────────────────────────────────────
# Main generate button (prominent & full-width)
# ──────────────────────────────────────────────
if st.button("🔄 Generate New Random Samples", type="primary", use_container_width=True):
    with st.spinner("Generating fresh random samples..."):
        # Fresh randomness every button press
        group_a = np.random.weibull(a=1.5, size=n) * 110      # Weibull shape 1.5 → mild wear-out
        group_b = np.random.exponential(scale=130, size=n)    # Exponential mean ≈ 130 hours
        
        # Store in session state so data persists across reruns
        st.session_state.group_a = group_a
        st.session_state.group_b = group_b
        st.session_state.generated = True
        st.session_state.n = n   # remember size used
    
    st.success(f"✅ New samples generated! (n = {n} per group)")

# ──────────────────────────────────────────────
# Display results only after first generation
# ──────────────────────────────────────────────
if st.session_state.get("generated", False):
    group_a = st.session_state.group_a
    group_b = st.session_state.group_b
    
    # Combine into DataFrame for easy stats & plotting
    df = pd.DataFrame({
        "Group A (Weibull)": group_a,
        "Group B (Exponential)": group_b
    })
    
    st.subheader("Summary Statistics")
    st.dataframe(df.describe().round(2), use_container_width=True)
    
    # Tabs for clean organization
    tab1, tab2, tab3 = st.tabs([
        "📊 Distributions (Histogram + KDE)",
        "📦 Box Plot Comparison",
        "📈 ECDF (Survival / Cumulative View)"
    ])
    
    with tab1:
        st.subheader("Histogram + Kernel Density Estimate")
        hist_data = [group_a, group_b]
        group_labels = ['Group A (Weibull)', 'Group B (Exponential)']
        fig_hist = ff.create_distplot(
            hist_data,
            group_labels,
            show_hist=True,
            show_rug=False,
            bin_size=8
        )
        fig_hist.update_layout(
            xaxis_title="Time to Failure (hours)",
            yaxis_title="Density",
            height=500
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        st.subheader("Boxplot Comparison")
        df_melt = df.melt(var_name="Group", value_name="Time to Failure (hours)")
        fig_box = px.box(
            df_melt,
            x="Group",
            y="Time to Failure (hours)",
            color="Group",
            points="all",
            notched=True
        )
        fig_box.update_layout(height=500)
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.subheader("Empirical Cumulative Distribution Function (ECDF)")
        # Fixed: use px.ecdf (most compatible & clean)
        df_melt = df.melt(var_name="Group", value_name="Time to Failure (hours)")
        fig_ecdf = px.ecdf(
            df_melt,
            x="Time to Failure (hours)",
            color="Group",
            markers=True
        )
        fig_ecdf.update_layout(
            xaxis_title="Time to Failure (hours)",
            yaxis_title="Cumulative Probability",
            height=500
        )
        st.plotly_chart(fig_ecdf, use_container_width=True)
    
    # CSV download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download current samples as CSV",
        data=csv,
        file_name="time_to_failure_samples.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("👉 Click the **Generate New Random Samples** button above to start the demonstration!")

# Footer
st.caption(
    "✅ Each button press creates brand-new random samples.\n"
    "Data is stored in Streamlit session state so plots stay visible until you generate again."
)
