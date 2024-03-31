import json
import os

from nostr_dvm.interfaces.dvmtaskinterface import DVMTaskInterface, process_venv
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.definitions import EventDefinitions
from nostr_dvm.utils.dvmconfig import DVMConfig, build_default_config
from nostr_dvm.utils.nip88_utils import NIP88Config
from nostr_dvm.utils.nip89_utils import NIP89Config, check_and_set_d_tag
from nostr_dvm.utils.nostr_utils import get_referenced_event_by_id, get_event_by_id, get_events_by_ids
from nostr_sdk import Tag, Kind


class TextSummarizationHuggingChat(DVMTaskInterface):
    KIND: Kind = EventDefinitions.KIND_NIP90_SUMMARIZE_TEXT
    TASK: str = "summarization"
    FIX_COST: float = 0
    dependencies = [("nostr-dvm", "nostr-dvm"), ("hugchat", "hugchat")]

    def __init__(self, name, dvm_config: DVMConfig, nip89config: NIP89Config, nip88config: NIP88Config = None,
                 admin_config: AdminConfig = None, options=None):
        dvm_config.SCRIPT = os.path.abspath(__file__)
        super().__init__(name=name, dvm_config=dvm_config, nip89config=nip89config, nip88config=nip88config,
                         admin_config=admin_config, options=options)

    def create_request_from_nostr_event(self, event, client=None, dvm_config=None):
        request_form = {}
        prompt = "A bill of rights is a written a list of rights freedoms of citizens of country. It is designed to recognize, protect and preserve the dignity of people. It is therefore an important part of Kenya’s constitution. The bill is guidance for ensuring that no citizen is treated unfairly. The right to life is a basic right. Every person has a right to live. The life of a person begins at conception. Abortion is, therefore not permitted except in cases where the life of a mother is in danger. It is therefore a crime to take another person’s life. Every person is equal before the law, and has the right to equal protection and benefits of the law. Before the law, therefore should be no difference with regard to a person’s sex, religion, political affiliation, race or status in society. The law should be applied in all cases equally. For instance, if the law states that punishment for stealing is imprisonment that should be applied in all cases whether the person who has stolen is a Christian or Hindu, male or female, master or servant. The state shall not discriminate directly or indirectly against any person on any basis including race, sex, pregnancy, marital status, health status, ethnic or social origin, colour, age, disability, religion, conscience, belief, culture, dress, language or birth. People should not discriminate directly or indirectly against others on the same bases. For instance, if a student performs well in the Kenya Certificate of Primary Education (KCPE), they should not be denied admission to secondary school because of their religion, race or culture. The state will therefore, take specific measures to ensure that people are not discriminated against. Women and men have the right to equal treatment including the right to equal opportunities in political, economic, cultural and social activities. In addition, both men and women have an equal right to inherit or have access to and manage property. Any law, culture, custom or tradition that undermines the dignity, welfare, interest or status of women or men is prohibited. For instance, although in some cultures all property including land belongs to men, the constitution states that women have a right to own property. By law, women in such a community can insist on their right to own land and property. In the proposed revised constitution of Kenya, the state shall take measures to ensure that women and their rights are protected. The state shall also provide reasonable facilities and opportunities to ensure that women realize their full potential and advance in the society.The youth constitute an important part of the society and are entitled to enjoy all rights and freedoms set out in the bill of rights, taking into account their unique needs. The state shall try to ensure that the youth have access to quality and relevant education, training and employment. The youth shall also be given a chance to participate in governance. The state shall also ensure that the youth have enough chances in the social, political, economic as well as other areas of national life. The youth, like other citizens have a right to associate with others to further their interests within the limits of the law. They are also entitled to protection from any culture, custom, tradition or practice that undermines their dignity or quality of life. They should lead a life free from exploitation, discrimination or abuse. It is the duty of every state to observe respect, protect, promote and fulfill the rights and freedoms of the citizens. Laws, policies and other measures should be used to ensure that this rights and freedoms are recognized. A person has the right to complain to the commission of human rights and administrative justice, and take legal action if the rights or freedom are violated, infringed or denied."
        for tag in event.tags():
            if tag.as_vec()[0] == 'i' and tag.as_vec()[2] == "text":
                # Extract text from input tags of type "text"
                prompt += tag.as_vec()[1] + "\n"
        options = {"prompt": prompt}
        request_form['options'] = json.dumps(options)
        return request_form

    def process(self, request_form):
        from hugchat import hugchat
        from hugchat.login import Login
        sign = Login(os.getenv("HUGGINGFACE_EMAIL"), os.getenv("HUGGINGFACE_PASSWORD"))
        cookie_path_dir = "./cookies_snapshot"
        try:
            cookies = sign.loadCookiesFromDir(cookie_path_dir)  # This will detect if the JSON file exists, return cookies if it does and raise an Exception if it's not.
        except:
            cookies = sign.login()
            sign.saveCookiesToDir(cookie_path_dir)

        options = DVMTaskInterface.set_options(request_form)

        try:
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            query_result = chatbot.query("Summarize the following notes: " + options["prompt"])
            return str(query_result["text"]).lstrip()

        except Exception as e:
            print("Error in Module: " + str(e))
            raise Exception(e)


def build_example(name, identifier, admin_config):
    dvm_config = build_default_config(identifier)
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    nip89info = {
        "name": name,
        "image": "https://image.nostr.build/720eadc9af89084bb09de659af43ad17fec1f4b0887084e83ac0ae708dfa83a6.png",
        "about": "I use a LLM connected via Huggingchat to summarize Inputs",
        "encryptionSupported": True,
        "cashuAccepted": True,
        "nip90Params": {}
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY, nip89info["image"])
    nip89config.CONTENT = json.dumps(nip89info)

    return TextSummarizationHuggingChat(name=name, dvm_config=dvm_config, nip89config=nip89config,
                                        admin_config=admin_config)


if __name__ == '__main__':
    
   

   
    # Prompt the user to enter the text
    print("Please enter the text to be summarized:")
    input_text = input()




    # Create configurations
    dvm_config = build_default_config("text_summarization")
    admin_config = AdminConfig()
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    nip89info = {
        "name": "Text Summarizer",
        "image": "https://image.nostr.build/720eadc9af89084bb09de659af43ad17fec1f4b0887084e83ac0ae708dfa83a6.png",
        "about": "I use a large language model connected via Huggingchat to summarize text inputs.",
        "encryptionSupported": True,
        "cashuAccepted": True,
        "nip90Params": {}
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag("text_summarization", "Text Summarizer", dvm_config.PRIVATE_KEY, nip89info["image"])
    nip89config.CONTENT = json.dumps(nip89info)

    # Create an instance of TextSummarizationHuggingChat
    summarizer = TextSummarizationHuggingChat(name="Text Summarizer", dvm_config=dvm_config, nip89config=nip89config,
                                            admin_config=admin_config)

    # Create a request form with the input text
    request_form = {"options": json.dumps({"prompt": input_text})}

    # Process the request to generate the summary
    summary = summarizer.process(request_form)

    # Print the summary
    print("Generated Summary:")
    print(summary)
