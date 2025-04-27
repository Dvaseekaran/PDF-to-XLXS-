# Insurance Rule Extractor

This project extracts insurance rules from a PDF and generates a structured Excel file.

## How to Run

1. Install dependencies:

## Extraction Requirements

- **State**:  
  Fill with the state name (e.g., "Oklahoma"). Leave blank if missing.

- **Rule Code**:  
  Auto-generate sequential codes in the format R001, R002, R003, etc.

- **Insurance Class**:  
  Identify and fill with the insurance category (e.g., "General Insurance"). If not found, leave blank.

- **Notes**:  
  Extract the full text of each regulation/rule as a single entry.  
  *Group lines together to form complete sentences or rules, rather than splitting by every line break.*

- **Rules**:  
  Convert the extracted regulation into structured IF-ELSE logic.  
  *Aim for clear, logical statements (e.g., "IF [condition] THEN [action] ELSE [alternative]").*

- **Parameters**:  
  List all relevant numbers, percentages, amounts, thresholds, or variables found in the rule.  
  *Only include meaningful values (e.g., 10%, $500, 30 days). Remove extra punctuation or unrelated characters.*


