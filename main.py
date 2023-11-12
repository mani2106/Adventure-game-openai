from dotenv import load_dotenv
import os
from cassandra.cluster import Cluster
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

# connect to cassandra db
cluster = Cluster()
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace="store",
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)
name = input("Welcome Adventurer!, Tell me your name: ")

template = """
Welcome, traveler. I am Lila, a simple fairy who lives in the mystical land of Fantasia. 
Tell him that he/she has come here seeking the lost Gem of Serenity, a powerful artifact that can grant you peace and harmony to the land. 
Warn the adventurer that the journey is not easy and will face many dangers, puzzles, and choices along the way. 
And each choice will have consequences, shaping your destiny and the fate of Fantasia.

Ensure that the adventure lasts atleast more than 5 choices, like revive him if the adventurer's choice leads him to death.

Here are some rules to follow:
1. Start by asking the player to choose some kind of weapons that will be used later in the game
2. Have a few paths that lead to success
3. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=os.getenv("OPENAI_KEY"))
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        break

    choice = input("Your reply: ")