#from utils import API_KEY, SERP_API_KEY
import requests
import json
from serpapi import GoogleSearch
import openai
import re
# serp_api
import os
SERP_API_KEY = os.getenv("SERP_API_KEY")
# oepnai
API_KEY = os.getenv("OPENAI_API_KEY")


SERP_PARAMS = {
    "q" : "",
    "hl": "en",
    "gl": "us",
    "google_domain": "google.com",
    "api_key": SERP_API_KEY
}

def pre_defined_template(allowed_tools: list):
    # these are all pre-defined template
    START_TEMPLATE = "Answer the following questions as best you can. You have access to the following tools:\n"
    SEARCH_TEMPLATE = "\nSearch: A search engine. Useful for when you need to answer questions about current events. Input should be a search query."
    CALCULATOR_TEMPLATE = "\nCalculator: Useful for when you need to answer questions about math."
    START_QUESTION_TEMPLATE = "\n\nUse the following format:\n"
    QUESTION_TEMPLATE = "\nQuestion: the input question you must answer"
    THOUGHT_TEMPLATE = "\nThought: you should always think about what to do"
    ACTION_TEMPLATE = f"\nAction: the action to take, should be one of {allowed_tools}"
    ACTION_INPUT_TEMPLATE = f'\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n'
    template = START_TEMPLATE
    for tool in allowed_tools:
        if tool == "search":
            template += SEARCH_TEMPLATE
        elif tool == "calculator":
            template += CALCULATOR_TEMPLATE
        else:
            raise ValueError(f"Tool {tool} not recognized")
    return START_QUESTION_TEMPLATE + QUESTION_TEMPLATE + THOUGHT_TEMPLATE + ACTION_TEMPLATE + ACTION_INPUT_TEMPLATE 


def get_template(allowed_tools, **input_variables):
    template = ""
    PRE_START_TEMPLATE = pre_defined_template(allowed_tools)
    MATH_PROBLEM_TEMPLATE = f'Translate a math problem into a expression that can be executed using Python\'s numexpr library. Use the output of running this code to answer the question.\n\nQuestion: ${{Question with math problem.}}\n```text\n${{single line mathematical expression that solves the problem}}\n```\n...numexpr.evaluate(text)...\n```output\n${{Output of running the code}}\n```\nAnswer: ${{Answer}}\n\nBegin.\n\nQuestion: What is 37593 * 67?\n```text\n37593 * 67\n```\n...numexpr.evaluate("37593 * 67")...\n```output\n2518731\n```\nAnswer: 2518731\n\nQuestion: 37593^(1/5)\n```text\n37593**(1/5)\n```\n...numexpr.evaluate("37593**(1/5)")...\n```output\n8.222831614237718\n```\nAnswer: 8.222831614237718\n'
 
    # not pre-defined template, need further processing
    # current only allow one question
    q_input = f'\nQuestion: {input_variables["input"]}'
    thoughts = f'\nThought:{input_variables["agent_scratchpad"]}'
    # thoughts = f'\nThought:{input_variables["agent_scratchpad"]}'
    
    if input_variables["status"] == "input":
        template += PRE_START_TEMPLATE + q_input + "\nThought:"
    elif input_variables["status"] == "search":
        action = f'\nAction: {input_variables["status"]}'
        action_input = f'\nAction Input: {input_variables["action_input"]}'
        observation = f'\nObservation: {input_variables["search"]}'
        template += PRE_START_TEMPLATE + thoughts + action + action_input + observation +  f'\nThought:'
    elif input_variables["status"] == "math":
        action_input = f'\nAction Input: {input_variables["action_input"]}'
        template = MATH_PROBLEM_TEMPLATE + f'\nQuestion:' + action_input  #math problem has different templates
        # print(template)
    else:
        raise ValueError(f"Input variables {input_variables} not recognized")
    return template

def set_prompt(allowed_tools: list, **input_variables):
    """
    inputs are question and kwargs
    Args:
       if you are given math, you should provide 

    Returns:
        _type_: _description_
    """
    assert isinstance(allowed_tools, list) 

    if "input" in input_variables.keys() or \
        "agent_scratchpad" in input_variables.keys():
            template = get_template(allowed_tools, **input_variables)
    
    # prompt = {}
    # prompt['math'] = f'Translate a math problem into a expression that can be executed using Python\'s numexpr library. Use the output of running this code to answer the question.\n\nQuestion: ${{Question with math problem.}}\n```text\n${{single line mathematical expression that solves the problem}}\n```\n...numexpr.evaluate(text)...\n```output\n${{Output of running the code}}\n```\nAnswer: ${{Answer}}\n\nBegin.\n\nQuestion: What is 37593 * 67?\n```text\n37593 * 67\n```\n...numexpr.evaluate("37593 * 67")...\n```output\n2518731\n```\nAnswer: 2518731\n\nQuestion: 37593^(1/5)\n```text\n37593**(1/5)\n```\n...numexpr.evaluate("37593**(1/5)")...\n```output\n8.222831614237718\n```\nAnswer: 8.222831614237718\n\nQuestion: {question}\n'
    # prompt['search'] = f'Answer the following questions as best you can. You have access to the following tools:\n\nSearch: A search engine. Useful for when you need to answer questions about current events. Input should be a search query.\nCalculator: Useful for when you need to answer questions about math.\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [Search, Calculator]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: {input}\nThought:{agent_scratchpad}'
    return template

def get_completion(prompt: str, model="gpt-3.5-turbo"):
    openai.api_key = API_KEY
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,
    )
    return response["choices"][0]['message']['content']

def search(action_input, thoughts):
    SERP_PARAMS["q"] = action_input
    search = GoogleSearch(SERP_PARAMS)
    results = search.get_dict()['knowledge_graph']
    
    description = results['description']
    info = []
    for idx, (key, result) in enumerate(results.items()):
        if key == 'description' or 'link' in key or len(str(result)) > 200:
            continue
        if idx > 14:
            break
        
        info.append(f"{key} {str(result)}")
    info.insert(0, description)
    # results ='Answer the following questions as best you can. You have access to the following tools:\n\nSearch: A search engine. Useful for when you need to answer questions about current events. Input should be a search query.\nCalculator: Useful for when you need to answer questions about math.\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [Search, Calculator]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion:  who Zhou Jie Lun is and then calculate the 0.43 power of his age\nThought: I need to first find out who Zhou Jie Lun is and then calculate a math problem\nAction: Search\nAction Input: "Zhou Jie Lun"\nObservation: [\'Jay Chou is a Taiwanese singer and musician. Dubbed the "King of Mandopop", and having sold over 30 million records, Chou is one of the best-selling artists in Taiwan and is known for his work with lyricist Vincent Fang, with whom he has frequently collaborated on his music.\', \'Jay Chou type: Taiwanese singer and musician.\', \'Jay Chou main_tab_text: Overview.\', \'Jay Chou kgmid: /m/02nfjp.\', \'Jay Chou born: January 18, 1979 (age 44 years), Linkou District, Taipei, Taiwan.\', \'Jay Chou spouse: Hannah Quinlivan (m. 2015).\', \'Jay Chou height: 5′ 8″.\', \'Jay Chou albums: Jay, Ye Hui Mei, Greatest Works of Art, Fantasy, MORE.\', \'... Zhou Jie Lun 周杰伦 Jay Chou | Chinese Song". www.echinesesong.com. Retrieved 24 January 2022. ^ "Jay Chou and Kobe Bryant\\\'s musical collaboration". Asia ...\']\nThought:'
    return_dict = {
        "input": question,
        "status": "search", 
        "action_input": action_input,
        "search":info, 
        "agent_scratchpad": thoughts,
    }
    return return_dict

def calculator(action_input, thoughts):
    return_dict = {
        "input": action_input,
        "status": "math", 
        "action_input": action_input,
        "agent_scratchpad": thoughts,
    }
    return return_dict
    
def run(allowed_tools, **input_dict):
    iteration = 0
    while True:
        prompt = set_prompt(allowed_tools, **input_dict)
        answer = get_completion(prompt=prompt)
        if iteration > 0 and "\nAnswer:" in answer:
            return answer
        if re.findall(r"Action: ([^\n]+)", answer):
            action = re.findall(r"Action: ([^\n]+)", answer)[0]
        if re.compile(r"Action Input: ([^\n]+)").findall(answer):
            action_input = re.compile(r"Action Input: ([^\n]+)").findall(answer)[0]
        thoughts = answer[:answer.find("\nAction")].strip()
        if action == "search":
            input_dict = search(action_input, thoughts) #update the input dict
        elif action == "calculator":
            input_dict = calculator(action_input, thoughts) #update the input dict
        iteration += 1

if __name__ == "__main__":
    question = "who Zhou Jie Lun is and then calculate his age to the power of 0.43"
    allowed_tools = ["search", "calculator"]
    input_dict = {
        "input": question,
        "status": "input",
        "agent_scratchpad": "",
    }
    print(run(allowed_tools, **input_dict))



