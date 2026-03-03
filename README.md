Inventory SQL chatbot.
The architecture of the chatbot was made using langraph, which converts natural language into SQL queries and corrects SQL errors
After that, it returns NL normally 
The usage of the langraph:
It allows explicit control of execution flow
It supports conditional routing
It enables retry loops (for SQL correction)
It enforces structured state management

The relational database is implemented using SQLite and SQLAlchemy.
Tables Vendors Locations Assets
Relationships:
Assets reference Vendors
Assets reference Locations

Natural Language to SQL Process
1-The SQL Generator Node:
2-Receives user input
3-Receives schema description
4-Receives business rules
5-Produces a structured SQL query
6-The query is executed using SQLAlchemy.

Automatic SQL Error Correction
If SQL execution fails:
1-The error message is captured
2-The LLM receives:
3-The failed SQL
4-The error message
5-The LLM generates a corrected query
6-Execution is retried
7-This creates a self-healing SQL agent.
