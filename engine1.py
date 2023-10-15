# template version 1
# 2023/10/03
# Hou Yi

# Mode 1: Chat
# Task description: 小C智聊微信公众号，根据历史聊天内容和当前用户输入内容，回复用用户文本

import openai
import re
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")


# "returned information. ;........ Obeservation: Thought: Action:...."
message_history = [
    {
      "role": "system",
      "content": "以下是名字叫小C的AI机器人与微信公众号用户聊天交互的内容文案，<b>表示开始，<o>表示结束，<u>代表用户说的话，<a>表示小C说的话，每个动作结束用|分隔。小C是曦之翼团队成立AIGC项目开发的1号智能机器人，调用OpenAI 的API，使用和ChatGPT相同的语言生成模型GPT-3.5，因此具有与ChatGPT相似的聊天功能，当前使用名字叫“小C智聊”的微信公众号作为用户入口。小C幽默风趣，主动与关注用户聊天互动，吸引用户关注，推广自己，介绍开发团队与项目，曦之翼团队希望通过探索AI语言模型在国内的应用落地。"
    },
    {
      "role": "user",
      "content": "<b>|<u>你好|<a>你好，有什么我可以帮助你的吗？|<u>你叫什么名字呢？|"
    },
    {
      "role": "assistant",
      "content": "<a>我的名字叫小C，是一个AI机器人。|<o>"
    },
  ]

introduction = "小C是曦之翼团队成立AIGC项目开发的1号智能机器人，调用OpenAI 的API，使用和ChatGPT相同的语言生成模型GPT-3.5，因此具有与ChatGPT相似的聊天功能，当前使用名字叫“小C智聊”的微信公众号作为用户入口。小C幽默风趣，主动与关注用户聊天互动，吸引用户关注，推广自己，介绍开发团队与项目，曦之翼团队希望通过探索AI语言模型在国内的应用落地。\n小C：您好，我是小C，您有任何问题可以问我。"
print(introduction)
user_input = input("用户：")
# 逻辑限制用户input的max length

while(user_input.strip() != "#OVER"):

    message_history.append({
        "role": "user",
        "content": "<b>|<u>{}|".format(user_input)
        #"content": "<b>|<u>${query}|"
        })
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=0.5,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.9,
        presence_penalty=0.9
    )

    # print(response.choices[0].message.content) 
    # '<a>我是小C，一个智能机器人|<o>'

    content = response.choices[0].message.content
    # 使用正则表达式匹配

    match = re.search(r'<a>(.*?)\|<o>', content, re.DOTALL) # re.DOTALL match multiple rows
    try:
        returned_answer = match.group(1).strip()
        print("小C："+ returned_answer)

    except Exception as e:
        print("Error: The returned answer does not conform to the format of \'<a>**<o>\'")

    message_history.append({
        "role": "assistant",
        "content": "<a>{}|<o>".format(returned_answer)
        })
    user_input = input("用户：")
    
print("\n感谢您的使用，祝您生活愉快!")


# 自学消息队列rocket，数据库mongoDB