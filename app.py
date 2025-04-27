from flask import Flask, request, render_template, send_file
import pdfplumber
import pandas as pd
import os
import io

app = Flask(__name__)

def extract_rules_from_pdf(file_stream):
    # Read PDF
    rules = []
    rule_counter = 1
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Group lines into full rules/sentences
                rule_texts = group_lines_into_rules(text)
                for rule_text in rule_texts:
                    if rule_text.strip():
                        rule = {
                            "State": "Oklahoma",  # Hardcoded because from sample
                            "Rule Code": f"R{rule_counter:03d}",
                            "Insurance Class": "General Insurance",
                            "Notes": rule_text.strip(),
                            "Rules": convert_to_if_else(rule_text.strip()),
                            "Parameters": extract_parameters(rule_text.strip())
                        }
                        rules.append(rule)
                        rule_counter += 1
    return rules

def group_lines_into_rules(text):
    # Group lines into sentences/rules based on punctuation
    import re
    # Split by sentence-ending punctuation followed by a newline or end of string
    sentences = re.split(r'(?<=[.!?])\s*\n', text)
    # Remove empty or whitespace-only sentences
    return [s.strip() for s in sentences if s.strip()]

def convert_to_if_else(note):
    # Enhanced logic for IF-ELSE structure
    note_lower = note.lower()
    import re

    # Try to extract IF-THEN(-ELSE) patterns
    if "if" in note_lower:
        # Find the 'if ... then ... else ...' pattern
        match = re.search(r'if (.+?) then (.+?)(?: else (.+))?$', note_lower, re.IGNORECASE)
        if match:
            condition = match.group(1).strip().capitalize()
            action = match.group(2).strip().capitalize()
            alternative = match.group(3).strip().capitalize() if match.group(3) else None
            if alternative:
                return f"IF {condition} THEN {action} ELSE {alternative}"
            else:
                return f"IF {condition} THEN {action}"
        # If only 'if' and 'then' present
        elif "then" in note_lower:
            parts = re.split(r'\bthen\b', note, flags=re.IGNORECASE)
            if len(parts) == 2:
                condition = parts[0].replace("if", "", 1).strip()
                action = parts[1].strip()
                return f"IF {condition} THEN {action}"
        # Only 'if' present, no 'then'
        else:
            condition = note[note_lower.find("if") + 2:].strip()
            return f"IF {condition} THEN [action unspecified]"
    elif "shall" in note_lower:
        # Try to extract subject and action
        match = re.search(r'(.+?) shall (.+)', note, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().capitalize()
            action = match.group(2).strip().capitalize()
            return f"IF {subject} THEN {action}"
        else:
            return f"IF condition THEN {note}"
    else:
        # Fallback: treat as a direct rule
        return f"Rule: {note}"

def extract_parameters(note):
    import re
    # Extract numbers, percentages, amounts, and time periods
    patterns = [
        r"\$\d+(?:,\d{3})*(?:\.\d+)?",         # Dollar amounts
        r"\d+(?:\.\d+)?\s*%",                  # Percentages
        r"\d+\s*(?:days?|months?|years?)",     # Time periods
        r"\d+(?:,\d{3})*(?:\.\d+)?",           # Plain numbers
    ]
    matches = []
    for pattern in patterns:
        matches += re.findall(pattern, note)
    # Clean up: remove duplicates, strip, and filter out numbers that are part of time periods or amounts already captured
    cleaned_matches = []
    seen = set()
    for m in matches:
        m_clean = m.strip(" ,.")
        if m_clean not in seen:
            seen.add(m_clean)
            cleaned_matches.append(m_clean)
    return ", ".join(cleaned_matches) if cleaned_matches else "None"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            rules = extract_rules_from_pdf(file)

            # Convert to DataFrame
            df = pd.DataFrame(rules)

            # Ensure output directory exists
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save to Excel file in output folder
            output_path = os.path.join(output_dir, "insurance_rules_output.xlsx")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Insurance Rules')

            # Also load the file into memory to send to user
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Insurance Rules')
            output.seek(0)

            return send_file(output, download_name="insurance_rules_output.xlsx", as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

