import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import shapiro, mannwhitneyu
import numpy as np
import plotly.express as px
import scipy.stats as stats
import matplotlib.pyplot as plt

st.set_page_config(page_title="A/B Testing Dashboard", page_icon="📊", layout="wide")
st.title("Marketing A/B Testing & Funnel Analysis")
st.markdown("An interactive dashboard to evaluate campaign efficiency and identify funnel bottlenecks.")

@st.cache_data
def load_data():
    df_control = pd.read_csv("cleaned_data\cleaned_control.csv")
    df_test = pd.read_csv("cleaned_data\cleaned_test.csv")
    return df_control, df_test

df_control, df_test = load_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["General Overview", "Data Exploration", "Funnel Analysis", "Statistical Testing", "Business Recommendation"])

# -- Tab 1:  The General Overview (Problem Statement and Dataset Overview) --
with tab1:
    st.header("Problem Statement")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(r"fig\AB_pic.png", use_container_width=True)
    st.markdown("""
    A company recently ran a 30-day A/B test to evaluate a new marketing campaign (Test Group) against their existing strategy (Control Group). 
    
    While the marketing team noticed a slight increase in total purchases from the new campaign, they also noticed it cost more to run. The business needs to know:
    
    1. Did the Test campaign actually perform better, or was the increase just random luck?
    2. Is the new campaign financially efficient?
    3. Where are users dropping off in the purchasing journey?
    
    This dashboard walks through the end-to-end data science process used to answer these questions and deliver a final launch recommendation.
    """)
    
    st.markdown("---")
    
    st.header("Dataset Overview")
    st.write("The dataset records daily customer interactions across both campaigns, tracking the complete end-to-end user journey (Impressions -> Reach -> Clicks -> Searches -> View Content -> Add to Cart -> Purchase).")
    
    with st.expander("View Data Dictionary"):
        st.markdown("""
            The features in the dataset:
            * Campaign Name: The name of the campaign
            * date: Date of the record
            * spend_usd: Amount spent on the campaign in dollars
            * number_of_impressions: Number of impressions the ad crossed through the campaign
            * reach: The number of unique impressions received in the ad
            * number_of_clicks: Number of website clicks received through the ads
            * number_of_searches: Number of users who performed searches on the website
            * number_of_view_content: Number of users who viewed content and products on the website
            * number_of_add_to_cart: Number of users who added products to the cart
            * number_of_purchase: Number of purchases
            
            The two campaigns that were performed by the company:
            * Control Campaign (Control Group)
            * Test Campaign (Test Group)
        """)
        
    st.subheader("Data Preview (Control Group)")
    st.dataframe(df_control.head(5), use_container_width=True)
    st.subheader("Data Preview (Test Group)")
    st.dataframe(df_test.head(5), use_container_width=True)

    st.caption("¹ Data Source: [Kaggle - A/B Testing Dataset](https://www.kaggle.com/datasets/amirmotefaker/ab-testing-dataset/data)")

# -- Tab 2: EDA (Money Spent, Purchases, Concluding EDA) --
with tab2:
    st.header("Campaign Overview (30-Day Totals)")
    
    # 1. The Conclusion of the EDA
    col1, col2 = st.columns(2)
    ctrl_spend = df_control['spend_usd'].sum()
    test_spend = df_test['spend_usd'].sum()
    ctrl_purchases = df_control['number_of_purchase'].sum()
    test_purchases = df_test['number_of_purchase'].sum()
    
    ctrl_cpa = ctrl_spend / ctrl_purchases
    test_cpa = test_spend / test_purchases
    
    with col1:
        st.subheader("Control Campaign")
        st.metric("Total Spend", f"${ctrl_spend:,.0f}")
        st.metric("Total Purchases", f"{ctrl_purchases:,.0f}")
        st.metric("Cost Per Acquisition (CPA)", f"${ctrl_cpa:.2f}")

    with col2:
        st.subheader("Test Campaign")
        spend_delta = ((test_spend - ctrl_spend) / ctrl_spend) * 100
        purch_delta = ((test_purchases - ctrl_purchases) / ctrl_purchases) * 100
        cpa_delta = ((test_cpa - ctrl_cpa) / ctrl_cpa) * 100
        
        st.metric("Total Spend", f"${test_spend:,.0f}", f"+{spend_delta:.1f}% vs Control", delta_color="inverse")
        st.metric("Total Purchases", f"{test_purchases:,.0f}", f"+{purch_delta:.1f}% vs Control")
        st.metric("Cost Per Acquisition (CPA)", f"${test_cpa:.2f}", f"+{cpa_delta:.1f}% vs Control", delta_color="inverse")
        
    st.info("-> Insight: The Test campaign generated slightly more purchases, but the cost scaled much faster, resulting in a more expensive Customer Acquisition Cost.")
    st.caption("Note: Cost per acquisition (CPA) is a marketing metric that measures the total money spent to get a single paying customer or user action. ")
    
    st.markdown("---")
    
    df_combined = pd.concat([df_control, df_test])
    
    # 2. USD Spent on Each Group
    st.subheader("Purchase Trends")
    c_line_purch, c_bar_purch = st.columns([3, 1])
    
    with c_line_purch:
        fig_purch_line = px.line(df_combined, x='date', y='number_of_purchase', color='campaign_name', 
                                 title='Daily Purchases Over Time', color_discrete_map={"Control Campaign": "#1f77b4", "Test Campaign": "#ff7f0e"})
        st.plotly_chart(fig_purch_line, use_container_width=True)
    
    with c_bar_purch:
        fig_purch_bar = px.bar(x=['Control', 'Test'], y=[ctrl_purchases, test_purchases], color=['Control', 'Test'],
                               title='Total Purchases', color_discrete_map={"Control": "#1f77b4", "Test": "#ff7f0e"})
        fig_purch_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Purchases")
        st.plotly_chart(fig_purch_bar, use_container_width=True)

    st.info("-> Insight: The test group shows higher USD spent than the control group with a jump of 6% in expense for the test group.")

    st.markdown("---")

    # 3. Comparing Number of Purchases
    st.subheader("Ad Spend Trends")
    c_line_spend, c_bar_spend = st.columns([3, 1])
    
    with c_line_spend:
        fig_spend_line = px.line(df_combined, x='date', y='spend_usd', color='campaign_name', 
                                 title='Daily Spend (USD) Over Time', color_discrete_map={"Control Campaign": "#1f77b4", "Test Campaign": "#ff7f0e"})
        st.plotly_chart(fig_spend_line, use_container_width=True)
        
    with c_bar_spend:
        fig_spend_bar = px.bar(x=['Control', 'Test'], y=[ctrl_spend, test_spend], color=['Control', 'Test'],
                               title='Total Spend (USD)', color_discrete_map={"Control": "#1f77b4", "Test": "#ff7f0e"})
        fig_spend_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Spend ($)")
        st.plotly_chart(fig_spend_bar, use_container_width=True)
        
    st.info("-> Insight: The test group shows higher purchases than the control group with a jump of 2% in purchases for the test group.")

# -- Tab 3: Funnel Analysis --
with tab3:
    st.header("Step-by-Step Funnel Drop-off")
    
    stages = ["Impressions", "Reach", "Clicks", "Searches", "View Content", "Add to Cart", "Purchase"]
    
    # Aggregate data for funnel
    ctrl_vols = [df_control['number_of_impressions'].sum(), df_control['reach'].sum(), df_control['number_of_clicks'].sum(), 
                 df_control['number_of_searches'].sum(), df_control['number_of_view_content'].sum(), 
                 df_control['number_of_add_to_cart'].sum(), df_control['number_of_purchase'].sum()]
                 
    test_vols = [df_test['number_of_impressions'].sum(), df_test['reach'].sum(), df_test['number_of_clicks'].sum(), 
                 df_test['number_of_searches'].sum(), df_test['number_of_view_content'].sum(), 
                 df_test['number_of_add_to_cart'].sum(), df_test['number_of_purchase'].sum()]
    
    def calculate_step_conversion(volume_list):
        rates = [100.0]
        for i in range(1, len(volume_list)):
            current_val = volume_list[i]
            previous_val = volume_list[i-1]
            rate = (current_val / previous_val) * 100 if previous_val > 0 else 0.0
            rates.append(round(rate, 2))
        return rates
    
    funnel_df = pd.DataFrame({
        'Stage': stages,
        'Control_Volume': ctrl_vols,
        'Test_Volume': test_vols,
        'Control_Conversion_From_Prev_%': calculate_step_conversion(ctrl_vols),
        'Test_Conversion_From_Prev_%': calculate_step_conversion(test_vols)
    })
    st.dataframe(funnel_df, use_container_width=True)
    st.caption("***Note: This table isolates the exact percentage of users who survive from one step to the next.***")
    
    st.markdown("---")
    
    fig = go.Figure()
    fig.add_trace(go.Funnel(name='Control Campaign', y=stages, x=ctrl_vols, textinfo="value+percent previous", marker={"color": "#1f77b4"}))
    fig.add_trace(go.Funnel(name='Test Campaign', y=stages, x=test_vols, textinfo="value+percent previous", marker={"color": "#ff7f0e"}))
    fig.update_layout(title_text="Funnel Drop-off Analysis: Control vs. Test", title_x=0.5, funnelmode="group")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("-> Bottleneck Identified: Notice the drop-off from 'View Content' to 'Add to Cart'. The Test group drops to 47.4% retention, while Control maintains 66.8%. This suggests the Test ad is 'clickbaity' but fails to deliver on the landing page.")

# -- TAB 4: Hypothesis Testing (Normality, Significant Tests) --
with tab4:
    st.header("Hypothesis Testing")
    st.write("Does the 2% increase in purchases for the Test group actually mean anything statistically?")
    
    df_control['cvr'] = (df_control['number_of_purchase'] / df_control['number_of_impressions']).fillna(0).replace([np.inf, -np.inf], 0)
    df_test['cvr'] = (df_test['number_of_purchase'] / df_test['number_of_impressions']).fillna(0).replace([np.inf, -np.inf], 0)

    # 1. Normality Checking
    st.subheader("1. Assumption Checking (Normality)")
    stat_ctrl, p_ctrl = shapiro(df_control['cvr'])
    stat_test, p_test = shapiro(df_test['cvr'])
    
    col3, col4 = st.columns(2)
    col3.metric("Control Shapiro p-value", f"{p_ctrl:.4f}")
    col4.metric("Test Shapiro p-value", f"{p_test:.4f}")
    st.caption("Because the Test p-value < 0.05, the data is NOT normally distributed. We must use a Non-Parametric test.")
    
    st.write("**Visual Normality Check (Q-Q Plots)**")
    st.write("We can see that the Test Group failed the normality check since its p-value < 0.05 and the QQ plot shows that the points does not fall near to the reference line. Therefore, we won't use t-test as it assumes normality. Hence, we will proceed  with Mann-Whitney U Test and Bootstrapping")
    
    qq_col1, qq_col2 = st.columns(2)

    # Control group normality check
    with qq_col1:
        osm_c, osr_c = stats.probplot(df_control['cvr'], dist="norm", fit=False)
        (slope_c, intercept_c, r_c) = stats.probplot(df_control['cvr'], dist="norm", fit=True)[1]
        
        fig_qq_ctrl = go.Figure()
        fig_qq_ctrl.add_trace(go.Scatter(x=osm_c, y=osr_c, mode='markers', marker=dict(color='#1f77b4'), name='Control CVR'))
        fig_qq_ctrl.add_trace(go.Scatter(x=[min(osm_c), max(osm_c)], y=[slope_c*min(osm_c) + intercept_c, slope_c*max(osm_c) + intercept_c], mode='lines', line=dict(color='red', dash='dash'), name='Fit'))
        fig_qq_ctrl.update_layout(title="Control Group Q-Q Plot", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", showlegend=False, height=400)
        st.plotly_chart(fig_qq_ctrl, use_container_width=True)

    # Test group normality check
    with qq_col2:
        osm_t, osr_t = stats.probplot(df_test['cvr'], dist="norm", fit=False)
        (slope_t, intercept_t, r_t) = stats.probplot(df_test['cvr'], dist="norm", fit=True)[1]

        fig_qq_test = go.Figure()
        fig_qq_test.add_trace(go.Scatter(x=osm_t, y=osr_t, mode='markers', marker=dict(color='#ff7f0e'), name='Test CVR'))
        fig_qq_test.add_trace(go.Scatter(x=[min(osm_t), max(osm_t)], y=[slope_t*min(osm_t) + intercept_t, slope_t*max(osm_t) + intercept_t], mode='lines', line=dict(color='red', dash='dash'), name='Fit'))
        fig_qq_test.update_layout(title="Test Group Q-Q Plot", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", showlegend=False, height=400)
        st.plotly_chart(fig_qq_test, use_container_width=True)
        
    st.markdown("---")

    # 2. Non-Parametric Test (Mann-Whitney U Test)
    st.subheader("2. Mann-Whitney U Test")
    u_stat, p_val = mannwhitneyu(df_test['cvr'], df_control['cvr'], alternative='greater')

    col1_stats, col2_stats = st.columns(2)

    with col1_stats:
        st.metric("P-Value", f"{p_val:.4f}")

    with col2_stats:
        st.metric("Test Statistic", f"{u_stat}")
    
    if p_val < 0.05:
        st.success("Result: Statistically Significant! The Test campaign truly performed differently.")
    else:
        st.warning("Result: NOT Statistically Significant (p > 0.05). The 2% lift in purchases is likely just random daily variance.")

    st.markdown("---")

    # 3. Bootstrapping
    st.subheader("3. Bootstrapping Simulation (10,000 Iterations)")
    st.write("To double-check our results without relying on distribution assumptions, we simulate 10,000 A/B tests by resampling our data. We then calculate a 95% Confidence Interval for the difference between the two campaigns.")
    
    np.random.seed(42)
    diff_observed = df_test['cvr'].mean() - df_control['cvr'].mean()

    boot_diffs = []
    for _ in range(10000):
        boot_control = np.random.choice(df_control['cvr'], size=len(df_control), replace=True)
        boot_test = np.random.choice(df_test['cvr'], size=len(df_test), replace=True)
        boot_diffs.append(np.mean(boot_test) - np.mean(boot_control))

    ci_lower = np.percentile(boot_diffs, 2.5)
    ci_upper = np.percentile(boot_diffs, 97.5)

    col5, col6, col7 = st.columns(3)
    col5.metric("Observed Difference in Mean CVR", f"{diff_observed:.4%}")
    col6.metric("95% CI Lower Bound", f"{ci_lower:.4%}")
    col7.metric("95% CI Upper Bound", f"{ci_upper:.4%}")

    if ci_lower > 0:
        st.success("Result: Statistically Significant! The 95% CI does not include 0.")
    else:
        st.warning("Result: Not Statistically Significant. The 95% CI includes 0, meaning the true difference could be zero or negative.")

    fig_boot = px.histogram(x=boot_diffs, nbins=50, title="Bootstrapped Differences (Test CVR - Control CVR)", color_discrete_sequence=['#9467bd'])
    fig_boot.add_vline(x=0, line_width=3, line_dash="dash", line_color="red", annotation_text="Zero Difference (Null)")
    fig_boot.add_vline(x=ci_lower, line_width=2, line_dash="dot", line_color="green", annotation_text="Lower 95% CI")
    fig_boot.add_vline(x=ci_upper, line_width=2, line_dash="dot", line_color="green", annotation_text="Upper 95% CI")
    fig_boot.update_layout(xaxis_title="Difference in Mean Conversion Rate", yaxis_title="Frequency")
    st.plotly_chart(fig_boot, use_container_width=True)

# -- Tab 5: Concluding Remarks and Recommendation --
with tab5:
    st.header("Executive Summary & Recommendation")
    
    st.markdown("""
    ### 1. Do not scale the Test Campaign
    Although the Test campaign generated a slight 2% lift in raw purchases, it required a 6% increase in ad spend. Statistical testing confirmed this 2% lift was insignificant, meaning the Test campaign effectively raised our Cost Per Acquisition (CPA) without delivering guaranteed results.

    ### 2. Next Steps: The Hybrid Approach
    The funnel analysis revealed two distinct truths:
    1. The Test Ad Creative is superior. It generated an 11.28% Click-Through Rate (CTR) vs the Control's 5.99%. It is able to significantly capture attention.
    2. The Control Landing Page is superior. It retained 67% of users at the Add-to-Cart stage, whereas the Test Campaign loses their users (dropping to 47%).
    
    Recommendation: We should launch a new test combining the highly engaging Test Ad Creative to drive top-of-funnel traffic, but route those users into the Control landing page experience to secure the conversions.
    """)

    st.markdown("---")
    
    # -- Simulator Calculator --
    st.header("Campaign Funnel & Profit Simulator")
    st.write("Instead of guessing a total conversion rate, use this calculator to simulate how improving specific stages of the funnel impacts the final profit.")
    st.caption("The default sliders are preset to our Hybrid recommendation.")
    
    # Default Inputs
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    
    with sim_col1:
        budget = st.number_input("Planned Budget ($)", min_value=100.0, value=3000.0, step=100.0)
    with sim_col2:
        impressions = st.number_input("Expected Impressions", min_value=1000, value=100000, step=5000)
    with sim_col3:
        aov = st.number_input("Average Order Value (AOV) in $", min_value=1.0, value=50.0, step=5.0)

    st.markdown("#### Adjust Funnel Conversion Rates")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        ctr = st.slider("1. Click-Through Rate (Impressions → Clicks)", min_value=0.1, max_value=25.0, value=11.28, step=0.1, format="%.2f%%")
        view_rate = st.slider("2. View Rate (Clicks → View Content)", min_value=1.0, max_value=100.0, value=40.0, step=1.0, format="%.2f%%")
    with col_s2:
        cart_rate = st.slider("3. Add-to-Cart Rate (View Content → Cart)", min_value=1.0, max_value=100.0, value=66.88, step=1.0, format="%.2f%%")
        purchase_rate = st.slider("4. Closing Rate (Cart → Purchase)", min_value=1.0, max_value=100.0, value=50.0, step=1.0, format="%.2f%%")

    # Step-by-step Funnel
    est_clicks = int(impressions * (ctr / 100))
    est_views = int(est_clicks * (view_rate / 100))
    est_carts = int(est_views * (cart_rate / 100))
    est_purchases = int(est_carts * (purchase_rate / 100))
    
    # Financial Math
    est_revenue = est_purchases * aov
    est_profit = est_revenue - budget
    est_cpa = budget / est_purchases if est_purchases > 0 else 0
    
    # Output Display
    st.markdown("#### Projected Financial Results")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    
    res_col1.metric("Est. Purchases", f"{est_purchases:,}")
    res_col2.metric("Target CPA", f"${est_cpa:,.2f}")
    res_col3.metric("Est. Revenue", f"${est_revenue:,.2f}")

    if est_profit >= 0:
        res_col4.metric("Est. Profit", f"${est_profit:,.2f}", "Profitable")
    else:
        res_col4.metric("Est. Profit", f"${est_profit:,.2f}", "-Loss", delta_color="red")