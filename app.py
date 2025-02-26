
import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import random

# Configure page
st.set_page_config(page_title="SafarNama", page_icon="✈️", layout="wide")

# Styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #5D6D7E;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .highlight {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<div class='title'><u><strong>✈️ Safarnama- Smart Trip Planner ✈️</strong></u></div>", unsafe_allow_html=True)

# Initialize session state for storing trip information
if 'trips' not in st.session_state:
    st.session_state.trips = []
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = {}
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Plan"

# Function to initialize Gemini API
def initialize_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini API: {e}")
        return None

# API Key configuration
with st.sidebar:
    api_key="AIzaSyDJNmx7PKmb92aHcrwBK7L5IKHipNzjVck"
    os.environ["GOOGLE_API_KEY"] = api_key
    st.session_state.gemini_model = initialize_gemini(api_key)
    if st.session_state.gemini_model:
        st.session_state.api_key_set = True
    else:
        st.error("Failed to initialize Gemini API. Please check your API key.")
    
    st.markdown("---")
    st.header("Navigation")
    if st.button("Plan Trip", key="nav_plan", use_container_width=True):
        st.session_state.active_tab = "Plan"
    if st.button("My Trips", key="nav_trips", use_container_width=True):
        st.session_state.active_tab = "Trips"
    if st.button("Expense Tracker", key="nav_expenses", use_container_width=True):
        st.session_state.active_tab = "Expenses"
    
    st.markdown("---")
    st.caption("<u>Made with your well wishes.❤️</u> ",unsafe_allow_html=True)

# Function to get AI recommendations
def get_recommendations(destination, duration, interests, budget, travelers):
    if not st.session_state.api_key_set:
        st.warning("Please set your Gemini API Key first.")
        return None
    
    try:
        prompt = f"""
        Create a comprehensive trip plan for {destination} for {duration} days.
        Budget: {budget}
        Number of travelers: {travelers}
        Interests: {', '.join(interests)}
        
        Please provide:
        1. A day-by-day itinerary with specific activities and places
        2. Recommended accommodations within budget
        3. Must-visit attractions based on the interests
        4. Local food recommendations
        5. Transportation tips
        6. Estimated costs for major categories (accommodation, food, activities, transportation)
        7. Essential travel tips for this destination
        
        Format the response as a structured JSON with the following keys:
        - itinerary (array of day objects with day_number, activities)
        - accommodations (array of options)
        - attractions (array of places)
        - food (array of recommendations)
        - transportation (object with tips)
        - costs (object with estimated costs per category)
        - tips (array of travel tips)
        """
        
        response = st.session_state.gemini_model.generate_content(prompt)
        try:
            # Try to extract JSON from the response
            content = response.text
            # Handle case where JSON might be within markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            trip_plan = json.loads(content)
            return trip_plan
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON from AI response: {e}")
            st.write("Raw response:", response.text)
            return None
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return None

# Function to save trips
def save_trip(trip_data):
    if 'id' not in trip_data:
        trip_data['id'] = len(st.session_state.trips) + 1
    
    if 'created_at' not in trip_data:
        trip_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    # Check if trip already exists (for updates)
    existing_trip_idx = None
    for i, trip in enumerate(st.session_state.trips):
        if trip.get('id') == trip_data.get('id'):
            existing_trip_idx = i
            break
    
    if existing_trip_idx is not None:
        st.session_state.trips[existing_trip_idx] = trip_data
    else:
        st.session_state.trips.append(trip_data)

# Function to generate sample expense data
def generate_expense_data(trip):
    expense_categories = ["Accommodation", "Food", "Transportation", "Activities", "Shopping", "Miscellaneous"]
    expenses = []
    
    # Calculate number of days
    duration = int(trip.get("duration", 7))
    start_date = datetime.strptime(trip.get("travel_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
    
    total_budget = float(trip.get("budget", 1000).replace("$", "").replace(",", ""))
    
    # Generate daily expenses
    for day in range(duration):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Generate 2-4 expenses per day
        num_expenses = random.randint(2, 4)
        for _ in range(num_expenses):
            category = random.choice(expense_categories)
            
            # Set amounts based on category
            if category == "Accommodation":
                amount = round(random.uniform(total_budget * 0.1, total_budget * 0.3) / duration, 2)
            elif category == "Food":
                amount = round(random.uniform(10, 100), 2)
            elif category == "Transportation":
                amount = round(random.uniform(5, 80), 2)
            elif category == "Activities":
                amount = round(random.uniform(15, 150), 2)
            elif category == "Shopping":
                amount = round(random.uniform(10, 200), 2)
            else:
                amount = round(random.uniform(5, 50), 2)
                
            description = f"{category} expense in {trip.get('destination')}"
            
            expenses.append({
                "date": date_str,
                "category": category,
                "description": description,
                "amount": amount,
                "trip_id": trip.get("id")
            })
    
    return expenses

# Function to view trip details
def show_trip_details(trip):
    st.subheader(f"Trip to {trip.get('destination', 'Unknown')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Duration:** {trip.get('duration', 'N/A')} days")
    with col2:
        st.write(f"**Budget:** {trip.get('budget', 'N/A')}")
    with col3:
        st.write(f"**Date:** {trip.get('travel_date', 'Not specified')}")
    
    st.write(f"**Travelers:** {trip.get('travelers', 'N/A')}")
    st.write(f"**Interests:** {', '.join(trip.get('interests', []))}")
    
    st.markdown("---")
    
    # Display itinerary
    if "itinerary" in trip and trip["itinerary"]:
        st.header("<u>Itinerary</u>",unsafe_allow_html=True)
        for day in trip["itinerary"]:
            with st.expander(f"Day {day.get('day_number', '?')}", expanded=False):
                activities = day.get("activities", [])
                if isinstance(activities, list):
                    for activity in activities:
                        st.write(f"• {activity}")
                else:
                    st.write(activities)
    
    # Display accommodations, attractions, and food in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if "accommodations" in trip and trip["accommodations"]:
            st.header("<u>Accommodations</u>",unsafe_allow_html=True)
            for acc in trip["accommodations"]:
                if isinstance(acc, dict) and "name" in acc:
                    st.write(f"• **{acc['name']}**")
                    if "price" in acc:
                        st.write(f"  Price: {acc['price']}")
                    if "description" in acc:
                        st.write(f"  {acc['description']}")
                else:
                    st.write(f"• {acc}")
            
        if "attractions" in trip and trip["attractions"]:
            st.header("<u>Must-Visit Attractions</u>",unsafe_allow_html=True)
            for attr in trip["attractions"]:
                if isinstance(attr, dict) and "name" in attr:
                    st.write(f"• **{attr['name']}**")
                    if "description" in attr:
                        st.write(f"  {attr['description']}")
                else:
                    st.write(f"• {attr}")
    
    with col2:
        if "food" in trip and trip["food"]:
            st.header("<u>Food Recommendations</u>",unsafe_allow_html=True)
            for food in trip["food"]:
                if isinstance(food, dict) and "name" in food:
                    st.write(f"• **{food['name']}**")
                    if "description" in food:
                        st.write(f"  {food['description']}")
                else:
                    st.write(f"• {food}")
                    
        if "transportation" in trip and trip["transportation"]:
            st.header("<u>Transportation Tips</u>",unsafe_allow_html=True)
            if isinstance(trip["transportation"], dict):
                for k, v in trip["transportation"].items():
                    st.write(f"• **{k.title()}:** {v}")
            elif isinstance(trip["transportation"], list):
                for item in trip["transportation"]:
                    st.write(f"• {item}")
            else:
                st.write(trip["transportation"])
    
    # Display costs and tips
    st.markdown("---")
    
    if "costs" in trip and trip["costs"]:
        st.header("<u>Estimated Costs</u>",unsafe_allow_html=True)
        cost_data = []
        
        if isinstance(trip["costs"], dict):
            for category, amount in trip["costs"].items():
                cost_data.append({"Category": category.title(), "Amount": amount})
        elif isinstance(trip["costs"], list):
            for item in trip["costs"]:
                if isinstance(item, dict) and "category" in item and "amount" in item:
                    cost_data.append({"Category": item["category"].title(), "Amount": item["amount"]})
                else:
                    st.write(f"• {item}")
        
        if cost_data:
            cost_df = pd.DataFrame(cost_data)
            
            # Create a cost breakdown visualization
            fig = px.pie(cost_df, values='Amount', names='Category', 
                         title='Cost Breakdown', 
                         color_discrete_sequence=px.colors.sequential.Viridis)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            # Display the cost table
            st.dataframe(cost_df, use_container_width=True)
    
    if "tips" in trip and trip["tips"]:
        st.header("<u>Travel Tips</u>",unsafe_allow_html=True)
        for tip in trip["tips"]:
            st.write(f"• {tip}")
    
    # Export button
    if st.button("Export Trip Details (JSON)"):
        trip_json = json.dumps(trip, indent=2)
        st.download_button(
            label="Download Trip JSON",
            data=trip_json,
            file_name=f"trip_to_{trip.get('destination', 'destination')}.json",
            mime="application/json"
        )

# Plan Trip Tab
if st.session_state.active_tab == "Plan":
    st.header("<u>Plan Your Trip</u>",unsafe_allow_html=True)
    
    with st.form("trip_form"):
        destination = st.text_input("Destination", value=st.session_state.current_trip.get("destination", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            travel_date = st.date_input("Travel Date", value=datetime.now())
            duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=st.session_state.current_trip.get("duration", 7))
        with col2:
            budget = st.text_input("Budget (USD)", value=st.session_state.current_trip.get("budget", "$1000"))
            travelers = st.number_input("Number of Travelers", min_value=1, max_value=20, value=st.session_state.current_trip.get("travelers", 2))
        
        interests = st.multiselect(
            "Interests",
            ["Sightseeing", "Food & Culinary", "Adventure", "History & Culture", "Nature", "Shopping", "Relaxation", "Nightlife", "Art & Museums"],
            default=st.session_state.current_trip.get("interests", ["Sightseeing", "Food & Culinary"])
        )
        
        submit_button = st.form_submit_button("Generate Trip Plan")
    
    if submit_button:
        if not destination:
            st.error("Please enter a destination.")
        elif not interests:
            st.error("Please select at least one interest.")
        else:
            # Save basic info to session state
            st.session_state.current_trip = {
                "destination": destination,
                "travel_date": travel_date.strftime("%Y-%m-%d"),
                "duration": duration,
                "budget": budget,
                "travelers": travelers,
                "interests": interests
            }
            
            with st.spinner("Generating your personalized trip plan..."):
                trip_plan = get_recommendations(destination, duration, interests, budget, travelers)
                
                if trip_plan:
                    # Combine user input with AI recommendations
                    full_trip = {**st.session_state.current_trip, **trip_plan}
                    save_trip(full_trip)
                    
                    st.session_state.current_trip = full_trip
                    st.success("Trip plan generated successfully!")
                    
                    # Display the generated plan
                    st.markdown("---")
                    show_trip_details(full_trip)

# My Trips Tab
elif st.session_state.active_tab == "Trips":
    st.header("<u>My Trips</u>",unsafe_allow_html=True)
    
    if not st.session_state.trips:
        st.info("You haven't planned any trips yet. Go to the 'Plan Trip' tab to create your first trip!")
    else:
        # Create trip cards
        for i, trip in enumerate(st.session_state.trips):
            with st.container():
                st.markdown(f"""
                <div class='card'>
                    <h3>{trip.get('destination', 'Trip')}</h3>
                    <p><strong>Date:</strong> {trip.get('travel_date', 'Not specified')}</p>
                    <p><strong>Duration:</strong> {trip.get('duration', 'N/A')} days</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View Details", key=f"view_{i}"):
                        st.session_state.current_trip = trip
                        st.session_state.view_trip_details = True
                with col2:
                    if st.button(f"Edit Trip", key=f"edit_{i}"):
                        st.session_state.current_trip = trip
                        st.session_state.active_tab = "Plan"
        
        if 'view_trip_details' in st.session_state and st.session_state.view_trip_details:
            st.markdown("---")
            show_trip_details(st.session_state.current_trip)
            if st.button("Back to Trips List"):
                st.session_state.view_trip_details = False
                st.experimental_rerun()

# Expense Tracker Tab
elif st.session_state.active_tab == "Expenses":
    st.header("<u>Expense Tracker</u>",unsafe_allow_html=True)
    
    if not st.session_state.trips:
        st.info("You haven't planned any trips yet. Go to the 'Plan Trip' tab to create your first trip!")
    else:
        # Trip selection
        trip_options = {f"{trip.get('destination')} ({trip.get('travel_date')})": i for i, trip in enumerate(st.session_state.trips)}
        selected_trip_name = st.selectbox("Select Trip", list(trip_options.keys()))
        selected_trip_idx = trip_options[selected_trip_name]
        selected_trip = st.session_state.trips[selected_trip_idx]
        
        # Initialize expenses for this trip if not already done
        if 'expenses' not in selected_trip:
            selected_trip['expenses'] = generate_expense_data(selected_trip)
            st.session_state.trips[selected_trip_idx] = selected_trip
        
        # Display expense summary
        total_spent = sum(expense['amount'] for expense in selected_trip['expenses'])
        budget = float(selected_trip.get('budget', '0').replace('$', '').replace(',', ''))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Budget", f"${budget:,.2f}")
        with col2:
            st.metric("Total Spent", f"${total_spent:,.2f}")
        with col3:
            remaining = budget - total_spent
            st.metric("Remaining", f"${remaining:,.2f}", delta=f"{(remaining/budget)*100:.1f}%" if budget > 0 else "N/A")
        
        # Expense visualization
        expense_data = pd.DataFrame(selected_trip['expenses'])
        
        # Group by category
        category_totals = expense_data.groupby('category')['amount'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(
                category_totals, 
                values='amount', 
                names='category',
                title='Expenses by Category',
                color_discrete_sequence=px.colors.qualitative.Pastel1
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Group by date
            expense_data['date'] = pd.to_datetime(expense_data['date'])
            daily_totals = expense_data.groupby(expense_data['date'].dt.strftime('%Y-%m-%d'))['amount'].sum().reset_index()
            
            fig2 = px.bar(
                daily_totals, 
                x='date', 
                y='amount',
                title='Daily Expenses',
                labels={'date': 'Date', 'amount': 'Amount (USD)'},
                color_discrete_sequence=['#2E86C1']
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Expense table with add/edit functionality
        st.subheader("Expense Details")
        
        # Add new expense form
        with st.expander("Add New Expense"):
            with st.form("add_expense_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_date = st.date_input("Date", value=datetime.now())
                    new_category = st.selectbox(
                        "Category", 
                        ["Accommodation", "Food", "Transportation", "Activities", "Shopping", "Miscellaneous"]
                    )
                with col2:
                    new_amount = st.number_input("Amount (USD)", min_value=0.0, step=0.01)
                    new_description = st.text_input("Description")
                
                add_expense = st.form_submit_button("Add Expense")
                
                if add_expense:
                    if not new_description:
                        st.error("Please enter a description.")
                    elif new_amount <= 0:
                        st.error("Amount must be greater than 0.")
                    else:
                        new_expense = {
                            "date": new_date.strftime("%Y-%m-%d"),
                            "category": new_category,
                            "description": new_description,
                            "amount": float(new_amount),
                            "trip_id": selected_trip.get("id")
                        }
                        
                        selected_trip['expenses'].append(new_expense)
                        st.session_state.trips[selected_trip_idx] = selected_trip
                        st.success("Expense added successfully!")
                        st.experimental_rerun()
        
        # Display expense table
        expense_df = pd.DataFrame(selected_trip['expenses'])
        if not expense_df.empty:
            expense_df = expense_df.sort_values(by='date', ascending=False)
            
            # Convert date column to datetime for better display
            expense_df['date'] = pd.to_datetime(expense_df['date']).dt.strftime('%Y-%m-%d')
            
            # Format amount column
            expense_df['amount'] = expense_df['amount'].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(
                expense_df[['date', 'category', 'description', 'amount']], 
                use_container_width=True,
                hide_index=True
            )
            
            # Export expenses
            if st.button("Export Expenses (CSV)"):
                csv = expense_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"expenses_{selected_trip.get('destination')}.csv",
                    mime="text/csv"
                )
