import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
from typing import Optional, Dict
import re


def normalize_query(question: str) -> str:
    """
    Normalize user queries to improve LLM understanding.
    Handles common patterns and informal phrasings.
    """
    question = question.strip()
    question_lower = question.lower()
    
    # Pattern 0: "How many X in each Y" -> "count X in each Y"
    how_many_grouped = r'^how many (\w+) in each (\w+)'
    match = re.match(how_many_grouped, question_lower)
    if match:
        item, group = match.groups()
        question = f"count {item} in each {group}"
    
    # Pattern 0b: "How many X" -> "count total number of X"
    elif question_lower.startswith('how many '):
        item = question_lower.replace('how many ', '').strip()
        question = f"count total number of {item}"
    
    # Pattern 0c: "How much is the total/average/sum X" -> "calculate total/average/sum of X"
    how_much_pattern = r'^how much is the (total|average|sum|mean) (\w+)'
    match = re.match(how_much_pattern, question_lower)
    if match:
        operation, column = match.groups()
        question = f"calculate the {operation} of {column}"
    
    # Pattern 0d: "What is the average/sum/total/mean of X" -> "calculate average of X"
    what_calc_pattern = r'^what is the (average|sum|total|mean|median|max|min|maximum|minimum) (?:of )?(\w+)'
    match = re.match(what_calc_pattern, question_lower)
    if match:
        operation, column = match.groups()
        if operation in ['max', 'maximum']:
            question = f"show the row where {column} is maximum"
        elif operation in ['min', 'minimum']:
            question = f"show the row where {column} is minimum"
        else:
            question = f"calculate the {operation} of {column}"
    
    # Pattern 0e: "What are the X" -> "show unique values in X column"
    what_are_pattern = r'^what are the (\w+)'
    match = re.match(what_are_pattern, question_lower)
    if match and 'unique' not in question_lower:
        column = match.group(1)
        question = f"show unique values in {column} column"
    
    # Pattern 0f: "Where is/are X" -> "show rows where"
    where_pattern = r'^where (?:is|are) (\w+)'
    match = re.match(where_pattern, question_lower)
    if match:
        condition = question_lower.replace('where is ', '').replace('where are ', '')
        question = f"show rows where {condition}"
    
    # Pattern 0g: "Can you show/give/get me X" -> "show X"
    can_you_pattern = r'^can you (show|give|get|find|display) (?:me )?(.+)'
    match = re.match(can_you_pattern, question_lower)
    if match:
        action, rest = match.groups()
        question = f"{action} {rest}"
    
    # Pattern 0h: "I want to see/know X" -> "show X"
    i_want_pattern = r'^i want to (see|know|find|get) (.+)'
    match = re.match(i_want_pattern, question_lower)
    if match:
        _, rest = match.groups()
        question = f"show {rest}"
    
    # Pattern 0i: "Tell me X" -> "show X"
    if question_lower.startswith('tell me '):
        rest = question_lower.replace('tell me ', '')
        question = f"show {rest}"
    
    # Pattern 0j: "Give me X" -> "show X"
    if question_lower.startswith('give me '):
        rest = question_lower.replace('give me ', '')
        question = f"show {rest}"
    
    # Pattern 1: "which/who has/have [highest/lowest/max/min] X" -> "show row where X is maximum/minimum"
    patterns_max_min = [
        (r'^(?:which|who|what)\s+(?:has|have)\s+(?:the\s+)?highest\s+(\w+)', r'show the row where \1 is maximum'),
        (r'^(?:which|who|what)\s+(?:has|have)\s+(?:the\s+)?lowest\s+(\w+)', r'show the row where \1 is minimum'),
        (r'^(?:which|who|what)\s+(?:has|have)\s+(?:the\s+)?max\s+(\w+)', r'show the row where \1 is maximum'),
        (r'^(?:which|who|what)\s+(?:has|have)\s+(?:the\s+)?min\s+(\w+)', r'show the row where \1 is minimum'),
    ]
    
    for pattern, replacement in patterns_max_min:
        match = re.match(pattern, question_lower)
        if match:
            question = re.sub(pattern, replacement, question_lower, flags=re.IGNORECASE)
            break
    
    # Pattern 2: "top N [by] X" -> "sort by X descending and show first N rows"
    top_pattern = r'^top\s+(\d+)\s+(?:by\s+)?(\w+)'
    match = re.match(top_pattern, question_lower)
    if match:
        n, column = match.groups()
        question = f"sort by {column} descending and show first {n} rows"
    
    # Pattern 3: "sort [the] top N by X" -> "sort by X descending and show first N rows"
    sort_top_pattern = r'^sort\s+(?:the\s+)?top\s+(\d+)\s+(?:by|rows by)\s+(\w+)'
    match = re.match(sort_top_pattern, question_lower)
    if match:
        n, column = match.groups()
        question = f"sort by {column} descending and show first {n} rows"
    
    # Pattern 4: Just a column name or "average X" -> "calculate average of X"
    if question_lower.startswith('average ') and len(question.split()) == 2:
        column = question.split()[1]
        question = f"calculate the average of {column}"
    
    # Pattern 5: "X department" or "X employees" -> "show rows where department equals X"
    dept_pattern = r'^(\w+)\s+(?:department|employees|workers)'
    match = re.match(dept_pattern, question_lower)
    if match and not question_lower.startswith('show'):
        dept = match.group(1)
        question = f"show all rows where department equals {dept}"
    
    # Pattern 6: "oldest/youngest/best" -> specific queries
    if question_lower in ['oldest', 'who is oldest', 'oldest employee', 'who is the oldest']:
        question = "show the row where age is maximum"
    elif question_lower in ['youngest', 'who is youngest', 'youngest employee', 'who is the youngest']:
        question = "show the row where age is minimum"
    elif question_lower in ['best performer', 'best employee', 'highest performer', 'who is the best']:
        question = "show the row where performance_score is maximum"
    
    # Pattern 7: Add "show" if query starts with a sorting/filtering word but no action
    action_words = ['show', 'display', 'get', 'find', 'calculate', 'list', 'count']
    if not any(question_lower.startswith(word) for word in action_words):
        if any(word in question_lower for word in ['sort', 'filter', 'where', 'group']):
            question = f"show {question}"
    
    # Pattern 8: Replace common abbreviations
    replacements = {
        ' exp ': ' experience ',
        ' perf ': ' performance ',
        ' dept ': ' department ',
        ' sal ': ' salary ',
        ' avg ': ' average ',
    }
    for old, new in replacements.items():
        question = question.replace(old, new)
    
    return question


class DataAnalysisAgent:
    """
    Wrapper around LangChain pandas dataframe agent.
    Uses Groq's Llama-3.3-70B model for natural language queries.
    """
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model_name = model_name
        self.agent = None
        self.df = None
    
    def initialize_agent(self, df: pd.DataFrame):
        """
        Create the pandas agent with the provided dataframe.
        """
        self.df = df
        
        llm = ChatGroq(
            temperature=0,
            model_name=self.model_name,
            groq_api_key=self.api_key
        )
        
        # Create agent with error handling and iteration limits
        self.agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type="zero-shot-react-description",
            handle_parsing_errors=True,
            max_iterations=10,
            allow_dangerous_code=True,  # Required for code execution
            prefix="""You are working with a pandas dataframe in Python named `df`. 

CRITICAL INSTRUCTIONS:
1. When asked to SHOW, DISPLAY, GET, or FIND data - you MUST return the actual dataframe/data using the python_repl_ast tool
2. NEVER just describe what you would do - ALWAYS execute the code and return results
3. ALWAYS use python_repl_ast to run code that returns the data
4. Your final answer MUST be the actual data (dataframe, number, series), NOT a string description
5. Use df.head(), df.tail(), df.sort_values(), df[...], etc. to return actual pandas objects
6. DO NOT use print() or str() - just return the dataframe/value directly

EXAMPLES OF CORRECT BEHAVIOR:
User: "show first 5 rows"
You: Action: python_repl_ast
Action Input: df.head(5)
Observation: [actual dataframe returned]
Final Answer: [return the dataframe object, not str(dataframe)]

User: "calculate average salary"  
You: Action: python_repl_ast
Action Input: df['salary'].mean()
Observation: 81266.67
Final Answer: 81266.67

User: "sort by age and show top 3"
You: Action: python_repl_ast
Action Input: df.sort_values('age', ascending=False).head(3)
Observation: [actual dataframe returned]
Final Answer: [return the dataframe, not its string representation]

NEVER DO THIS:
User: "show data"
You: "Here is the data: [description]"  ❌ WRONG

ALWAYS DO THIS:
User: "show data"  
You: [execute code, return actual dataframe object]  ✅ CORRECT

Remember: Return ACTUAL DATA OBJECTS, not string descriptions or print outputs!"""
        )
    
    def query(self, question: str) -> Dict[str, any]:
        """
        Execute a natural language query against the dataframe.
        Returns dict with 'success', 'result', and optional 'error'.
        """
        if self.agent is None:
            return {
                'success': False,
                'result': None,
                'error': 'Agent not initialized. Please upload a CSV first.'
            }
        
        try:
            # Normalize the query to handle common patterns
            normalized_question = normalize_query(question)
            
            # If normalization changed the query significantly, use normalized version
            if normalized_question != question and len(normalized_question) > len(question) * 0.7:
                question = normalized_question
            
            # Enhance question to ensure we get data back
            if any(word in question.lower() for word in ['show', 'display', 'get', 'find', 'sort', 'filter', 'calculate']):
                enhanced_question = question
            else:
                enhanced_question = f"Show me: {question}"
            
            result = self.agent.invoke(enhanced_question)
            
            # Extract the actual output - handle multiple formats
            if isinstance(result, dict):
                if 'output' in result:
                    output = result['output']
                elif 'result' in result:
                    output = result['result']
                else:
                    # Return the whole dict if no specific output key
                    output = result
            else:
                output = result
            
            # IMPORTANT: Check if output is a string that looks like a DataFrame
            # The agent sometimes returns str(dataframe) instead of the dataframe itself
            if isinstance(output, str) and 'employee_name' in output and '\n' in output:
                # This might be a stringified DataFrame - try to parse it back
                # For now, just return it as-is but flag it
                pass  # We'll handle display in the UI
            
            # Check if output is empty string or None
            if output is None or (isinstance(output, str) and not output.strip()):
                output = "Query executed successfully but returned no output."
            
            return {
                'success': True,
                'result': output,
                'error': None
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Clean up error messages for better UX
            if "Could not parse LLM output" in error_msg:
                error_msg = "The AI is having trouble understanding this query. Try using simpler phrasing like 'show first 5 rows' or 'calculate average salary'."
            elif "column" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = f"Column not found. Available columns are: {', '.join(self.df.columns.tolist())}"
            elif "parsing" in error_msg.lower():
                error_msg = "Query format issue. Try rephrasing more simply, like 'show rows where salary > 80000'."
            elif len(error_msg) > 200:
                # Truncate very long error messages
                error_msg = error_msg[:200] + "... (Try a simpler query)"
            
            return {
                'success': False,
                'result': None,
                'error': error_msg
            }
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the current dataframe."""
        return self.df
