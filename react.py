import os 
from langchain.agents import load_tools
from langchain.agents import AgentType
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.chains import LLMMathChain

# # 设置HTTP代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8080'

# # 设置HTTPS代理
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8080'

# 配置信任证书
os.environ['REQUESTS_CA_BUNDLE'] = '/Users/yihou/Documents/projects/ai_agent_23_10/certificates.pem'

# if os.path.exists(os.environ.get('REQUESTS_CA_BUNDLE')):
#     print("证书文件存在")
# else:
#     print("证书文件不存在")


key = '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'

llm = OpenAI(temperature=0, openai_api_key=key)
# serpapi_api_key = '3999fd790801bc6e48e53a4aef4e832d75cc6c4bc9af01db6506ebc63c4676de'
serpapi_api_key = os.getenv("SERP_API_KEY", '3999fd790801bc6e48e53a4aef4e832d75cc6c4bc9af01db6506ebc63c4676de')
# tools = load_tools(["serpapi", "llm-math"], llm=llm,serpapi_api_key=serpapi_api_key)

# agent = initialize_agent(tools,llm,agent='zero-shot-react-description',verbose=True)
tools = load_tools(["serpapi", "llm-math"], llm=llm,serpapi_api_key=serpapi_api_key)

agent = initialize_agent(tools,llm,agent='zero-shot-react-description',verbose=True)

agent.run(
    "谁是周杰伦? What is her current age raised to the 0.43 power?"
)
print()