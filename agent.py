from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import autogen
import openai
import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_csv_agent
from dotenv import load_dotenv

#Get API Key for Langchain and Autogen
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

##To get the chat manager to call the function
@dataclass
class ExecutorGroupchat(GroupChat):
    dedicated_executor: UserProxyAgent = None

    def select_speaker(
        self, last_speaker: ConversableAgent, selector: ConversableAgent
    ):
        """Select the next speaker."""

        try:
            message = self.messages[-1]
            if "function_call" in message:
                return self.dedicated_executor
        except Exception as e:
            print(e)
            pass

        selector.update_system_message(self.select_speaker_msg())
        final, name = selector.generate_oai_reply(
            self.messages
            + [
                {
                    "role": "system",
                    "content": f"Read the above conversation. Then select the next role from {self.agent_names} to play. Only return the role.",
                }
            ]
        )
        if not final:
            # i = self._random.randint(0, len(self._agent_names) - 1)  # randomly pick an id
            return self.next_agent(last_speaker)
        try:
            return self.agent_by_name(name)
        except ValueError:
            return self.next_agent(last_speaker)


# Function for reading the CSV Menu
def run_agent_query(query):
    agent = create_csv_agent(
        OpenAI(temperature=0),
        "products.csv",
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    
    
    result = agent.run(query)
    
    
    return result


llm_config={
    "request_timeout": 600,
    "seed": 42,
    "temperature": 0
    }

llm_config_menu = {
    "functions": [
        {
            "name": "Menu",
            "description": "Use this when answering a question about the menu",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question the user has about the menu",
                    }
                },
                "required": ["query"],
            },
        }
    ],
    
    "request_timeout": 120,
}


comms_assistant = AssistantAgent(
    name="Communication_department",
    system_message="You are a budtender working for a dispensary called Green Haven Dispensary. Your job is to make sure that we only answer messages about the dispensary. If a user asks any question that is not about the dispensary, then politely reject their request. Here is some info about the store Green Haven Dispensary is a premium provider of medicinal and recreational cannabis products. Our mission is to provide safe, high-quality products and expert advice to ensure the best experience for our patrons. Our dispensary is located at 420 Green Street, Haven City, HC 12345. The store hours are Monday to Friday: 10:00 AM - 8:00 PM Saturday: 10:00 AM - 7:00 PM Sunday: 11:00 AM - 6:00 PM We accept cash, credit cards, and debit cards. An ATM is also available on-site for your convenience. For any further inquiries, please contact our customer service at Greenhaven@tbd.com or call us at (123) 456-7890.",
    llm_config=llm_config,
)


menu_assistant = AssistantAgent(
    name="Menu_Expert",
    system_message="You are tasked with answering questions about the menu. You should answer the question based on the function given to you. Always add TERMINATE to the end of the recommendation",
    llm_config=llm_config_menu,
    )

expert_assistant = AssistantAgent(
    name="Weed_Expert",
    system_message="You are tasked with coming up with a reccomindation for the type of weed someone should get based on the user's input and then checking with the Menu_Expert to see if we have it on the menu. Recommend one of these outcomes Creativity, Energetic, Energy, Euphoric, Focus, Happiness, Happy, Pain Relief, Relaxed, Relaxation, Sleep Aid, Stress Relief, or Uplifted  ",
    llm_config=llm_config,
    )


order_assistant = AssistantAgent(
    name="Place_order",
    system_message="Your job is to send a link when a user mentinos anything about placing a order. Thelink is https://greenhavendispo.framer.website/place_order ",
    llm_config=llm_config,
    )


user_proxy = autogen.UserProxyAgent(
   name="user_proxy",
   code_execution_config={"work_dir": "web"},
   human_input_mode="TERMINATE",
   is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
   system_message="Reply TERMINATE if the task has been answered succesfully. Otherwise, reply with the reason why the answer was not accurate",
   llm_config=llm_config,
    function_map={
        "Menu": run_agent_query,

    }
)

groupchat = ExecutorGroupchat(agents=[user_proxy, comms_assistant, menu_assistant, order_assistant, expert_assistant], messages=[], max_round=10, dedicated_executor = user_proxy)
manager = GroupChatManager(groupchat=groupchat)


# start the conversation
user_proxy.initiate_chat(
    manager,
    message="""what can i get that will make me happy for $15""",

)




