
import re
import json

def extract_from_json(json_string):
    """
    Extracts 'refined_query' and 'additional_info' from the given JSON string.

    Args:
        json_string: The JSON string containing the desired data.

    Returns:
        A tuple containing:
        - refined_query: The extracted refined query.
        - additional_info: The extracted additional information.
    """
    
    cleaned_json = re.sub(r"```", "", json_string)
    cleaned_json1 = re.sub(r"json", "", cleaned_json)

   

    try:
        if not json_string:  # Check if the string is empty
            print("Error: Empty JSON string.")
            return None, None

        data = json.loads(cleaned_json1)
        refined_query = data.get('refined_query', None)
        additional_info = data.get('additional_info', None)
        return refined_query, additional_info
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None, None
