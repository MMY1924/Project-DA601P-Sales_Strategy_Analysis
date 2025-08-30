
"""
Interactive Choropleth Map Generator for Sales Strategy Analysis

This module generates an interactive choropleth map showing sales method
dominance by US state, extracted from the Sales Strategy Analysis project.

Author: Analytics Department AM analyst MMY14
Date: 2025-08-30
Python Version: 3.8+
"""

import pandas as pd
import plotly.express as px
from plotly.offline import plot


def load_sales_data(filepath: str) -> pd.DataFrame:
    """
    Load and preprocess sales data from CSV file.
    
    Args:
        filepath (str): Path to the product sales CSV file
        
    Returns:
        pd.DataFrame: Cleaned and preprocessed sales data
    """
    sales_data = pd.read_csv(filepath)
    
    # Standardize sales method categories
    sales_method_mapping = {
        'Email': 'Email',
        'Call': 'Call',
        'Email + Call': 'Email + Call',
        'em + call': 'Email + Call',
        'email': 'Email'
    }
    sales_data['sales_method'] = sales_data['sales_method'].map(
        sales_method_mapping
    )
    
    # Impute missing revenue values using method-specific means
    mean_revenue_by_method = sales_data.groupby('sales_method')['revenue'].mean()
    
    def replace_null_revenue(row):
        if pd.isnull(row['revenue']):
            return mean_revenue_by_method[row['sales_method']]
        return row['revenue']
    
    sales_data['revenue'] = sales_data.apply(replace_null_revenue, axis=1)
    
    # Fix business logic violations (customer tenure > 39 years)
    sales_data.loc[sales_data['years_as_customer'] > 39, 'years_as_customer'] = 39
    
    return sales_data


def calculate_geographic_dominance(sales_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sales method dominance by state.
    
    Args:
        sales_data (pd.DataFrame): Preprocessed sales data
        
    Returns:
        pd.DataFrame: State-level dominance analysis with abbreviations
    """
    # Calculate percentage breakdown by state
    state_method_pct = sales_data.groupby(['state', 'sales_method']).size().unstack(fill_value=0)
    state_method_pct = state_method_pct.div(state_method_pct.sum(axis=1), axis=0) * 100
    
    # Determine dominant method per state
    numeric_cols = ['Call', 'Email', 'Email + Call']
    state_method_pct['dominant_method'] = state_method_pct[numeric_cols].idxmax(axis=1)
    state_method_pct['dominance_strength'] = state_method_pct[numeric_cols].max(axis=1)
    
    # State abbreviation mapping for choropleth display
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 
        'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 
        'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 
        'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 
        'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 
        'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 
        'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    
    # Add state abbreviations
    choropleth_data = state_method_pct.reset_index()
    choropleth_data['state_abbrev'] = choropleth_data['state'].map(state_abbrev)
    
    return choropleth_data


def create_choropleth_map(choropleth_data: pd.DataFrame) -> None:
    """
    Generate and save interactive choropleth map.
    
    Args:
        choropleth_data (pd.DataFrame): State-level dominance data
    """
    fig = px.choropleth(
        choropleth_data,
        locations='state_abbrev',
        locationmode="USA-states",
        color='dominance_strength',
        color_continuous_scale='RdYlBu_r',
        scope="usa",
        title="Sales Method Dominance by State",
        labels={'dominance_strength': 'Dominance %'},
        hover_data=['state', 'dominant_method', 'Call', 'Email', 'Email + Call'],
        hover_name='state'
    )
    
    fig.update_layout(
        title_x=0.5,
        font=dict(size=14),
        width=1200,
        height=700
    )
    
    # Save as HTML file
    plot(fig, filename='sales_method_dominance_choropleth.html', auto_open=False)
    print("Interactive choropleth map saved as: sales_method_dominance_choropleth.html")
    
    # Display in notebook environment if available
    try:
        fig.show()
    except Exception:
        print("Map saved to HTML file. Open in browser to view interactively.")


def main():
    """
    Main execution function for generating the choropleth map.
    """
    try:
        # Load and preprocess data
        sales_data = load_sales_data('product_sales.csv')
        print(f"Loaded {len(sales_data)} customer records")
        
        # Calculate geographic dominance
        choropleth_data = calculate_geographic_dominance(sales_data)
        print(f"Calculated dominance metrics for {len(choropleth_data)} states")
        
        # Generate interactive map
        create_choropleth_map(choropleth_data)
        
    except FileNotFoundError:
        print("Error: product_sales.csv not found in Study/ directory")
    except Exception as e:
        print(f"Error generating choropleth map: {e}")


if __name__ == "__main__":
    main()
