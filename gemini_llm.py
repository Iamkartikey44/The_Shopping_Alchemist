import os
import google.generativeai as genai
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import streamlit as st
import pandas as pd
import json



GOOGLE_API_KEY = st.secrets['GOOGLE_API_KEY']

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Select the Gemini model you want to use (e.g., "gemini-1.5-flash")
model_name = "gemini-1.5-flash"  # Replace with your desired model name
model = genai.GenerativeModel(model_name)



#Define JSON output structure for structured response
class SerpAPIPromptResponse(BaseModel):
    refined_query:str = Field(description="Refined search query for the product search.")
    additional_info:str = Field(description="Additional adjectives summarized to be added to the search query.")

#JSON output parser
json_parser = JsonOutputParser(pydantic_object=SerpAPIPromptResponse)

#Granite LLM Prompt Template
granite_template = PromptTemplate(
    template="System: {system_prompt}\n{format_prompt}\nHuman:{user_prompt}\nAI.",
    input_variables= ["system_prompt","format_prompt","user_prompt"]

)

def llm_generate_gl(location):
    """
    Use the Gemini LLM to determine the ISO 3166-1 alpha-2 country code (gl) from a location string.

    Args:
        location (str): The location string to extract the country code from.

    Returns:
        str: The two-letter ISO 3166-1 alpha-2 country code (e.g., 'US') or None if invalid.
    """
    prompt = (
        "You are an expert at identifying ISO 3166-1 alpha-2 country codes from locations. "
        "Output only the two-letter country code (e.g., 'US' for United States) for the provided location, "
        "without any additional text or explanations.\nLocation: " + location
    )

    try:
        response = model.generate_content(prompt)
        gl_code = response.text.strip()  # Remove whitespace
        if len(gl_code) == 2 and gl_code.isalpha():  # Ensure valid ISO 3166-1 alpha-2 code
            return gl_code.upper()
        else:
            print(f"Invalid country code returned: {gl_code}")
            return None
    except Exception as e:
        print(f"Error in llm_generate_gl: {e}")
        return None

def refine_query(user_input, location):
    """
    Use Gemini LLM to refine user input for SerpAPI.

    Args:
        user_input (str): Raw input query from the user.
        location (str): Optional location for context (e.g., "New York").

    Returns:
        dict: A structured response containing the refined query and additional information (if applicable).
    """
    prompt = f"""
    You are a highly skilled shopping assistant. Refine user queries into specific product searches. 

    **User Input:** {user_input}

    **Location:** {location} 

    **Output:** 
    - **refined_query:** The refined search query.
    - **additional_info:** (Optional) Any additional information or adjectives to enhance the search.

    Please provide the output in JSON format.
    """

    try:
        response = model.generate_content(prompt)
        return response
    except Exception as e:
        print(f"Error in refine_query: {e}")
        return {}



#Result Comparison
def generate_comparison_table(products,featured_results=None,nearby_results=None):
    """
        Generate a comparison table for products, including deals and additional shopping details.
        Args:
            products (list): List of main shopping results.
            featured_results (list): List of featured shopping results (optional).
            nearby_results (list): List of nearby shopping results (optional).
        Returns:
            tuple: A tuple containing the comparison table as HTML and a detailed summary.
    """
    # Combine all products results (main+featured) for comparison
    all_products = products[:10]
    if featured_results:
        all_products += featured_results[:5] #Add top 5 featured results

    #Prepare product summaries
    product_summaries = [
        {
            "Name": f"<a href='{p.get('product_link', '#')}' target='_blank'>{p.get('title', 'N/A')}</a>",
            "Price Now": p.get("price", "N/A"),
            "Original Price": p.get("old_price", "N/A"),
            "Special Offer": ", ".join(p.get("extensions", [])) if p.get("extensions") else "No Discount",
            "Rating": f"{p.get('rating', 'N/A')} ⭐",
            "Reviews": f"{p.get('reviews', 'N/A')} Reviews",
            "Store": f"<img src='{p.get('source_icon', '#')}' alt='{p.get('source', 'N/A')}' style='height:20px;vertical-align:middle;'/> {p.get('source', 'N/A')}",
            "Delivery": p.get("delivery", "N/A"),
            "Image": f"<img src='{p.get('thumbnail', '#')}' alt='Product Image' style='height:50px;'/>"

        }
        for p in all_products
    ]    
    #Prepare product summaries
    product_summaries_llm = [
        {
            
            "Name": p.get("title", "N/A"),
            "Price Now": p.get("price", "N/A"),
            "Original Price": p.get("old_price", "N/A"),
            "Special Offer": ", ".join(p.get("extensions", [])) if p.get("extensions") else "No Discount",
            "Rating": f"{p.get('rating', 'N/A')}",
            "Reviews": f"{p.get('reviews', 'N/A')} Reviews",
            "Store": f"<img src='{p.get('source_icon', '#')}' alt='{p.get('source', 'N/A')}' style='height:20px;vertical-align:middle;'/> {p.get('source', 'N/A')}",
            "Delivery": p.get("delivery", "N/A"),
            #"Image": f"<img src='{p.get('thumbnail', '#')}' alt='Product Image' style='height:50px;'/>"
        }
        for p in all_products
    ]

    # Create a dataFrame for comparison
    comparison_df = pd.DataFrame(product_summaries)
    comparison_df_llm = pd.DataFrame(product_summaries_llm)

    if comparison_df.empty:
        return "No Products Found","<p>Summary Unavailable No product data available for analysis.</p>"
    
    summary_prompt = (
         "You are an intelligent and detail-oriented shopping assistant. Analyze the following products and generate a detailed summary. "
        "Your response should include the following sections formatted as valid HTML:"
        "<h4>Best Value Product</h4>: Identify the product with the best price-to-value ratio."
        "<h4>Highest Rated Option</h4>: Highlight the product with the highest user rating."
        "<h4>Unique Features</h4>: List any unique or distinctive features of specific products."
        "<h4>Trade-offs and Comparisons</h4>: Discuss trade-offs between products, considering price, ratings, and reviews."
        "<h4>Conclusion and Suggestion</h4>: Provide a clear recommendation and reasoning for the best product or approach."
        "Use <ul> for lists and <li> for each item. Ensure all HTML tags are properly closed."
        "Here is the product information:\n"
        f"{comparison_df_llm.to_dict(orient='records')}"
    )


    try:
        llm_result = model.generate_content([summary_prompt])
        if not llm_result.text:
            raise ValueError("LLM returned an empty response.")
        summary = llm_result.text #Extract the generated summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = "<p>Summary Unavailable An error occured while generating the summary. Please try again later.</p>"

    #Ensure all sections are included in the summary
    required_sections = [
        "Best Value Product",
        "Highest Rated Option",
        "Unique Features",
        "Trade-offs and Comparisons",
        "Conclusion and Suggestion",
    ]
    for section in required_sections:
        if section not in summary:
            summary +=f"\n{section}\n Data unavailable for this secion."

    #Convert the comparison DataFrame to an HTML table
    comparison_table_html = comparison_df.to_html(index=False,escape=False) #Disable escaping for links and images        


    return comparison_table_html,summary