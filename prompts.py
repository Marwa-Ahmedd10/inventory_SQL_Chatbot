INTENT_PROMPT = """
Classify the user input into one of:
- greeting
- query

User input: {input}

Return only one word.
"""


SQL_GENERATION_PROMPT = """
You are an SQL expert.

Database Schema:

vendors(id, name, status)
locations(id, name, city, status)
assets(id, name, category, status, vendor_id, location_id)

Business Rules:
- Only return records where status = 'Active'
- Exclude Retired and Disposed assets
- Only include inactive if explicitly requested

Generate ONLY the SQL query.

User question: {input}
"""