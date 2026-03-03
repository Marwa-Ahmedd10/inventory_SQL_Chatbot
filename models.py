from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    sql_query: Optional[str]
    result: Optional[str]
    error: Optional[str]