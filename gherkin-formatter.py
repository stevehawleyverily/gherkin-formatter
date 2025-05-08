import re

def clean_gherkin_text_simplified(raw_text: str) -> str:
    """
    Cleans and reformats Gherkin feature text, assuming no docstrings.

    This function addresses common formatting issues such as:
    - Extraneous double quotes surrounding entire Feature blocks.
    - Artifact trailing double quotes at the end of a Feature block.
    - Duplicate double quotes ("") within text, replacing them with a single (").
    - Inconsistent indentation of Gherkin keywords.

    It aims to preserve all textual content, including non-breaking spaces,
    and maintains the separation of multiple Feature definitions.
    """
    # Normalize line endings to \n for consistent processing
    raw_text = raw_text.replace('\r\n', '\n')

    # Regex to find feature blocks. A block starts with an optional quote,
    # then "Feature:", and extends non-greedily until the next Feature definition
    # or the end of the string. re.DOTALL makes '.' match newlines.
    feature_block_pattern = re.compile(r'(?P<block>"?Feature:.*?)(?=(?:"?Feature:|$))', re.DOTALL)
    
    processed_feature_blocks = []

    for match in feature_block_pattern.finditer(raw_text):
        # .strip() removes leading/trailing whitespace from the entire matched block
        block_text_stripped_outer = match.group('block').strip()
        
        cleaned_block_text = block_text_stripped_outer

        # 1. Handle block-level quoting artifacts
        if cleaned_block_text.startswith('"Feature:') and cleaned_block_text.endswith('"'):
            # Case: "Feature: ... entire block ... "
            cleaned_block_text = cleaned_block_text[1:-1]
        elif cleaned_block_text.startswith('Feature:') and cleaned_block_text.endswith('"'):
            # Case: Feature: ... entire block ... " (artifact quote at the end of block)
            cleaned_block_text = cleaned_block_text[:-1]
        
        lines_of_block = cleaned_block_text.split('\n')
        reformatted_lines_for_current_block = []
        
        for line_text in lines_of_block:
            # Rstrip() to clean trailing spaces from the line.
            processed_line_content = line_text.rstrip() 
            
            # --- Replace "" with " (unconditionally, as no docstrings to protect) ---
            processed_line_content = processed_line_content.replace('""', '"')
            # --- End Replacement ---
            
            # For keyword detection, lstrip standard spaces and tabs.
            temp_stripped_for_keyword = processed_line_content.lstrip(' \t')
            
            current_indent = "" # Default, should be overridden by keyword

            # Determine indentation based on Gherkin keywords
            if temp_stripped_for_keyword.startswith("Feature:"):
                current_indent = ""
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif temp_stripped_for_keyword.startswith("@"):
                current_indent = "  "
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif temp_stripped_for_keyword.startswith(("Scenario:", "Rule:", "Example:", "Background:")):
                current_indent = "  "
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif temp_stripped_for_keyword.startswith("Examples:"): # Keyword for Scenario Outline examples
                current_indent = "    "
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif temp_stripped_for_keyword.startswith("|"): # Table row
                current_indent = "      " 
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif temp_stripped_for_keyword.startswith(("Given", "When", "Then", "And", "But", "*")): # Step keywords
                current_indent = "    "
                reformatted_lines_for_current_block.append(current_indent + temp_stripped_for_keyword)
            elif not temp_stripped_for_keyword: # Empty line
                reformatted_lines_for_current_block.append("") # Preserve empty lines
            else: 
                # Fallback for lines that don't start with a known Gherkin keyword (e.g., comments, misformatted lines)
                # Preserve the line with its original relative indentation (after rstrip and "" replacement).
                reformatted_lines_for_current_block.append(processed_line_content) 

        if reformatted_lines_for_current_block or cleaned_block_text: # Add if block had content
            processed_feature_blocks.append("\n".join(reformatted_lines_for_current_block))
    
    # Join all processed feature blocks with two newlines for separation
    return "\n\n".join(processed_feature_blocks)

# Example usage:
if __name__ == "__main__":
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            file_content = f.read()
        cleaned_file_content = clean_gherkin_text_simplified(file_content)
        print(cleaned_file_content)
        # To save to a new file:
        with open("cleaned_output.md", "w", encoding="utf-8") as out_f:
            out_f.write(cleaned_file_content)
    except FileNotFoundError:
        print("Error: input.feature not found.")
    except Exception as e:
        print(f"An error occurred: {e}")