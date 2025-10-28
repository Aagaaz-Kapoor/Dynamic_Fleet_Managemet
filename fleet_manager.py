import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Dynamic Fleet Manager",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data and model artifacts
@st.cache_data
def load_data():
    # Load CSV files from project root (relative paths)
    orders = pd.read_csv('orders.csv')
    delivery_performance = pd.read_csv('delivery_performance.csv')
    routes = pd.read_csv('routes_distance.csv')
    vehicles = pd.read_csv('vehicle_fleet.csv')
    cost_breakdown = pd.read_csv('cost_breakdown.csv')
    customer_feedback = pd.read_csv('customer_feedback.csv')
    # warehouse_inventory = pd.read_csv('warehouse_inventory.csv')

    # Then try to load model artifacts
    try:
        model_artifacts = joblib.load('fleet_model_artifacts.pkl')
    except FileNotFoundError:
        st.warning("Model artifacts not found. Please run fleet_analysis.py first.")
        model_artifacts = {}

    # Return ALL data at the end
    return orders, delivery_performance, routes, vehicles, cost_breakdown, customer_feedback, model_artifacts

# Initialize session state
if 'optimized_assignments' not in st.session_state:
    st.session_state.optimized_assignments = None

# Main application
def main():
    st.title("🚚 Dynamic Fleet Manager")
    st.markdown("### Intelligent Vehicle-Order Matching System")
    
    # Load data
    orders, delivery_performance, routes, vehicles, cost_breakdown, customer_feedback, model_artifacts = load_data()
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "🔍 Order Matching", 
        "🚛 Fleet Overview", 
        "📈 Performance"
    ])
    
    with tab1:
        display_dashboard(orders, vehicles, delivery_performance, cost_breakdown)
    
    with tab2:
        display_order_matching(orders, vehicles, routes, model_artifacts)
    
    with tab3:
        display_fleet_overview(vehicles)
    
    with tab4:
        display_performance_metrics(delivery_performance, customer_feedback, cost_breakdown)

def display_dashboard(orders, vehicles, delivery_performance, cost_breakdown):
    st.header("Operations Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vehicles = len(vehicles)
        available_vehicles = len(vehicles[vehicles['Status'] == 'Available'])
        st.metric("Total Vehicles", total_vehicles, f"{available_vehicles} available")
    
    with col2:
        total_orders = len(orders)
        st.metric("Total Orders", total_orders)
    
    with col3:
        on_time_deliveries = len(delivery_performance[
            delivery_performance['Actual_Delivery_Days'] <= 
            delivery_performance['Promised_Delivery_Days']
        ])
        on_time_rate = (on_time_deliveries / len(delivery_performance)) * 100
        st.metric("On-Time Delivery Rate", f"{on_time_rate:.1f}%")
    
    with col4:
        numeric_costs = cost_breakdown.select_dtypes(include=[np.number])
        avg_delivery_cost = numeric_costs.sum(axis=1).mean()
        st.metric("Average Delivery Cost", f"₹{avg_delivery_cost:.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle status distribution
        status_counts = vehicles['Status'].value_counts()
        fig1 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Vehicle Status Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Order priority distribution
        priority_counts = orders['Priority'].value_counts()
        fig2 = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            title="Order Priority Distribution",
            labels={'x': 'Priority', 'y': 'Count'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Vehicle type distribution
        vehicle_type_counts = vehicles['Vehicle_Type'].value_counts()
        fig3 = px.bar(
            x=vehicle_type_counts.index,
            y=vehicle_type_counts.values,
            title="Vehicle Type Distribution",
            labels={'x': 'Vehicle Type', 'y': 'Count'}
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Delivery performance
        performance_counts = delivery_performance['Delivery_Status'].value_counts()
        fig4 = px.pie(
            values=performance_counts.values,
            names=performance_counts.index,
            title="Delivery Status Distribution"
        )
        st.plotly_chart(fig4, use_container_width=True)

def display_order_matching(orders, vehicles, routes, model_artifacts):
    st.header("Order-Vehicle Matching")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input Parameters")
        
        # Order selection
        selected_order_id = st.selectbox(
            "Select Order",
            options=orders['Order_ID'].unique()
        )
        
        selected_order = orders[orders['Order_ID'] == selected_order_id].iloc[0]
        
        # Display order details
        st.write("**Order Details:**")
        st.write(f"- Priority: {selected_order['Priority']}")
        st.write(f"- Product: {selected_order['Product_Category']}")
        st.write(f"- Origin: {selected_order['Origin']} → Destination: {selected_order['Destination']}")
        st.write(f"- Special Handling: {selected_order['Special_Handling']}")
        st.write(f"- Order Value: ₹{selected_order['Order_Value_INR']:.2f}")
        
        # Matching constraints
        st.subheader("Matching Constraints")
        min_score = st.slider("Minimum Match Score", 0, 100, 70)
        
        if st.button("Find Optimal Vehicle Match"):
            match_results = find_vehicle_matches(selected_order, vehicles, routes, min_score)
            st.session_state.optimized_assignments = match_results
    
    with col2:
        st.subheader("Vehicle Matching Results")
        
        if st.session_state.optimized_assignments is not None:
            results_df = st.session_state.optimized_assignments
            
            # Display best match
            if len(results_df) > 0:
                best_match = results_df.iloc[0]
                
                st.success(f"🎯 **Best Match Found!**")
                st.write(f"**Vehicle:** {best_match['Vehicle_ID']} ({best_match['Vehicle_Type']})")
                st.write(f"**Match Score:** {best_match['Score']}/100")
                st.write(f"**Location:** {best_match['Current_Location']}")
                st.write(f"**Capacity:** {best_match['Capacity_KG']:.0f} kg")
                st.write(f"**Fuel Efficiency:** {best_match['Fuel_Efficiency_KM_per_L']:.1f} km/L")
                
                # Show all matches in a table
                st.subheader("All Suitable Vehicles")
                display_df = results_df[['Vehicle_ID', 'Vehicle_Type', 'Score', 
                                       'Current_Location', 'Capacity_KG', 'Fuel_Efficiency_KM_per_L']]
                st.dataframe(display_df, use_container_width=True)
                
                # Visualization
                fig = px.bar(
                    results_df.head(10),
                    x='Vehicle_ID',
                    y='Score',
                    color='Vehicle_Type',
                    title="Top Vehicle Matches by Score"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No suitable vehicles found with the current constraints. Try lowering the minimum score.")
        else:
            st.info("Select an order and click 'Find Optimal Vehicle Match' to see results")

def find_vehicle_matches(order, vehicles_df, routes_df, min_score=70):
    """Find suitable vehicle matches for an order"""
    
    # Get route information
    order_route = routes_df[routes_df['Order_ID'] == order['Order_ID']]
    if len(order_route) == 0:
        return pd.DataFrame()
    
    route = order_route.iloc[0]
    
    # Constraint mapping (simplified)
    constraint_mapping = {
        'Temperature_Controlled': ['Refrigerated'],
        'Fragile': ['Small_Van', 'Medium_Truck', 'Refrigerated'],
        'Hazmat': ['Medium_Truck', 'Large_Truck'],
        'None': ['Small_Van', 'Medium_Truck', 'Large_Truck', 'Refrigerated', 'Express_Bike']
    }
    
    priority_requirements = {
        'Express': ['Express_Bike', 'Small_Van'],
        'Standard': ['Small_Van', 'Medium_Truck'],
        'Economy': ['Medium_Truck', 'Large_Truck']
    }
    
    matches = []
    available_vehicles = vehicles_df[vehicles_df['Status'] == 'Available']
    
    for _, vehicle in available_vehicles.iterrows():
        score = 0
        
        # Special handling compatibility (40 points)
        special_handling = order['Special_Handling']
        if special_handling in constraint_mapping:
            if vehicle['Vehicle_Type'] in constraint_mapping[special_handling]:
                score += 40
        
        # Priority compatibility (30 points)
        priority = order['Priority']
        if vehicle['Vehicle_Type'] in priority_requirements[priority]:
            score += 30
        
        # Capacity check (20 points)
        capacity_required = min(order['Order_Value_INR'] / 100, 1000)
        if vehicle['Capacity_KG'] >= capacity_required:
            score += 20
        elif vehicle['Capacity_KG'] >= capacity_required * 0.7:
            score += 10
        
        # Location proximity (10 points)
        if vehicle['Current_Location'] == order['Origin']:
            score += 10
        
        if score >= min_score:
            match_data = vehicle.to_dict()
            match_data['Score'] = score
            matches.append(match_data)
    
    results_df = pd.DataFrame(matches)
    if len(results_df) > 0:
        results_df = results_df.sort_values('Score', ascending=False)
    
    return results_df

def display_fleet_overview(vehicles):
    st.header("Fleet Overview & Management")
    
    # Fleet statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Fleet Size", len(vehicles))
    
    with col2:
        available_count = len(vehicles[vehicles['Status'] == 'Available'])
        st.metric("Available Vehicles", available_count)
    
    with col3:
        avg_age = vehicles['Age_Years'].mean()
        st.metric("Average Vehicle Age", f"{avg_age:.1f} years")
    
    # Interactive fleet table
    st.subheader("Fleet Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_types = st.multiselect(
            "Filter by Vehicle Type",
            options=vehicles['Vehicle_Type'].unique(),
            default=vehicles['Vehicle_Type'].unique()
        )
    
    with col2:
        selected_status = st.multiselect(
            "Filter by Status",
            options=vehicles['Status'].unique(),
            default=vehicles['Status'].unique()
        )
    
    with col3:
        min_efficiency = st.slider(
            "Minimum Fuel Efficiency (km/L)",
            min_value=float(vehicles['Fuel_Efficiency_KM_per_L'].min()),
            max_value=float(vehicles['Fuel_Efficiency_KM_per_L'].max()),
            value=float(vehicles['Fuel_Efficiency_KM_per_L'].min())
        )
    
    # Apply filters
    filtered_fleet = vehicles[
        (vehicles['Vehicle_Type'].isin(selected_types)) &
        (vehicles['Status'].isin(selected_status)) &
        (vehicles['Fuel_Efficiency_KM_per_L'] >= min_efficiency)
    ]
    
    st.dataframe(filtered_fleet, use_container_width=True)
    
    # Fleet analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # Fuel efficiency by vehicle type
        fig1 = px.box(
            vehicles,
            x='Vehicle_Type',
            y='Fuel_Efficiency_KM_per_L',
            title="Fuel Efficiency by Vehicle Type"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # CO2 emissions analysis
        fig2 = px.scatter(
            vehicles,
            x='Age_Years',
            y='CO2_Emissions_Kg_per_KM',
            color='Vehicle_Type',
            size='Capacity_KG',
            title="CO2 Emissions vs Vehicle Age"
        )
        st.plotly_chart(fig2, use_container_width=True)

def display_performance_metrics(delivery_performance, customer_feedback, cost_breakdown):
    st.header("Performance Metrics & Analytics")
    
    # Delivery performance analysis
    st.subheader("Delivery Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delivery delay analysis
        delivery_performance['Delay_Days'] = (
            delivery_performance['Actual_Delivery_Days'] - 
            delivery_performance['Promised_Delivery_Days']
        )
        
        fig1 = px.histogram(
            delivery_performance,
            x='Delay_Days',
            title="Delivery Delay Distribution",
            nbins=20
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Carrier performance
        carrier_performance = delivery_performance.groupby('Carrier').agg({
            'Actual_Delivery_Days': 'mean',
            'Customer_Rating': 'mean',
            'Delivery_Cost_INR': 'mean'
        }).reset_index()
        
        fig2 = px.scatter(
            carrier_performance,
            x='Actual_Delivery_Days',
            y='Customer_Rating',
            size='Delivery_Cost_INR',
            color='Carrier',
            title="Carrier Performance: Delivery Time vs Customer Rating"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Customer feedback analysis
    st.subheader("Customer Feedback Analysis")
    
    if not customer_feedback.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            rating_dist = customer_feedback['Rating'].value_counts().sort_index()
            fig3 = px.bar(
                x=rating_dist.index,
                y=rating_dist.values,
                title="Customer Rating Distribution",
                labels={'x': 'Rating', 'y': 'Count'}
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            issue_dist = customer_feedback['Issue_Category'].value_counts()
            fig4 = px.pie(
                values=issue_dist.values,
                names=issue_dist.index,
                title="Issue Category Distribution"
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    # Cost analysis
    st.subheader("Cost Analysis")
    
    # Calculate total cost per order using only numeric columns
    numeric_costs = cost_breakdown.select_dtypes(include=[np.number])
    total_cost_series = numeric_costs.sum(axis=1)
    cost_breakdown['Total_Cost'] = total_cost_series
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost component breakdown (numeric columns only, excluding Total_Cost)
        components_numeric = cost_breakdown.select_dtypes(include=[np.number]).copy()
        if 'Total_Cost' in components_numeric.columns:
            components_numeric = components_numeric.drop(columns=['Total_Cost'])
        cost_components = components_numeric.mean()
        fig5 = px.pie(
            values=cost_components.values,
            names=cost_components.index,
            title="Average Cost Breakdown"
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Total cost distribution
        fig6 = px.histogram(
            cost_breakdown,
            x='Total_Cost',
            title="Total Cost Distribution",
            nbins=20
        )
        st.plotly_chart(fig6, use_container_width=True)

if __name__ == "__main__":
    main()