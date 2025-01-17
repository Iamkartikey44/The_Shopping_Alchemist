from gemini_llm import refine_query, generate_comparison_table
from serp_ai import search_products
from utils import extract_from_json

import streamlit as st

st.set_page_config(page_title="AI Shopping Assistant", page_icon="🛍️", layout='centered', initial_sidebar_state="expanded")

# Inject CSS for custom styling
custom_css = """
<style>
/* Apply the background image to the Streamlit app container */

div.stTextInput p {
    font-size: 1.2rem; /* Half the size of a typical 2.5rem heading */
    line-height: 1.6;
    font-family: serif;
    color: black; /* Neutral shade for good readability on light/dark backgrounds */
    margin: 9px 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); /* Slight shadow for depth */
}

/* Additional Styling for Specific Paragraphs */
div.stTextInput p.highlight {
    font-size: 1.3rem;
    color: #2b6cb0; /* Accent blue for important notes */
    font-weight: bold;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25); /* Deeper shadow for emphasis */
}

/* Title Styling */
h1 {
    text-align: center;
    font-size: 2.5rem;
    color: #000000;
    /*background-color: rgba(255, 255, 255, 0.8);*/
    padding: 20px 40px;
    border-radius: 10px;
    /*box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);*/
    margin-top: 20px;
}

/* Summary Section */
h3 {
    font-size: 1.8rem;
    font-weight: bold;
    color: #ffffff;
    background: linear-gradient(to right, #6a11cb0a, #2575fc80);
    padding: 10px 20px;
    border-radius: 8px;
    text-align: center;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
    margin-top: 20px;
}


h4#best-value-product {
   font-family:emoji;
   color:mediumvioletred;
}
h4#highest-rated-option{
   font-family:emoji;
   color:mediumvioletred;
}
h4#unique-features{
   font-family:emoji;
   color:mediumvioletred;
}
h4#trade-offs-and-comparisons{
   font-family:emoji;
   color:mediumvioletred;
}

h4#conclusion-and-suggestion{
   font-family:emoji;
   color:mediumvioletred;
}


/* Input Fields */
div.stTextInput label {
    font-weight: bold;
    color: #555;
    font-size: 1rem;
}

div.stTextInput input {
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

div.stTextInput input:focus {
    border-color: #007bff;
    box-shadow: 0 0 4px rgba(0, 123, 255, 0.3);
}

/* Button Styling */
div.stButton button {
    background-color: #2193c996;
    color: white;
    font-weight: bold;
    font-size: 1rem;
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

div.stButton button:hover {
    background-color: #e180198a;
    font-weight: bold;
    color: black;

}

/* Results Section */
.results {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin: 20px 0;
}

.results h2 {
    color: #444;
    font-size: 1.5rem;
    border-bottom: 2px solid #007bff;
    padding-bottom: 8px;
}

.results p {
    line-height: 1.6;
    color: #555;
}

/* Table Styling */

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    font-size: 0.95rem;
    color: #333;
}

table th, table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

table th {
    background-color: #455a64f0;
    color: #fff;
    font-weight: bold;
}

table tr:nth-child(even) {
    background-color: #f1f1f1;
}

table tr:hover {
    background-color: #e9ecef;
    color: #000; 
}
</style>
"""

# Apply the CSS
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🛍️ Welcome to Your AI Shopping Assistant")

# Sidebar
query = st.sidebar.text_input("What are you looking for?", placeholder="Enter your search query, e.g., gift for my parents or simply a product name")

location = st.sidebar.text_input("Enter City, State/Country (optional):", placeholder="e.g., Austin, Texas, India")
include_summary = st.sidebar.checkbox("Include Summary", value=True)

if st.sidebar.button("Search for the Best Options and Summarize"):
    if query:
        with st.spinner("Searching and summarizing..."):
            try:
                refined_query_response = refine_query(query, location)
                refined_query_response = extract_from_json(refined_query_response.text)
                refined_query = f"{refined_query_response[0]} {refined_query_response[1]}".strip()
                refined_query = f"Refined query for {query} in location : {location}"

                # Fetch products using SerpAPI
                products = search_products(refined_query, location=location)

                if not products:
                    st.error("No products found for your query. Please refine your search and try again.")
                else:
                    comparison_table, summary = generate_comparison_table(products)

                    
                    st.markdown("<h3>Here are some great options:</h3>",unsafe_allow_html=True)
                    st.markdown(comparison_table, unsafe_allow_html=True)
                    
                    if include_summary:
                        st.subheader("Smart Shopping Insights")
                        st.write("Here's a summary to help you make the best choice:")
                        st.markdown(summary, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred while processing your request: {e}")
    else:
        st.warning("Please enter a query to search.")
