import google.generativeai as genai
from typing import TypedDict, Literal
import glob
import os
import sys
import pyttsx3
import time
import json
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from train_parkeet import get_text,delete_Audio
from controll_mail import filter_emails


gen_api = "AIzaSyDFcmAXIaCP-RyNhdOzJg-eSZtDEsikgcQ"
genai.configure(api_key=gen_api)
model = genai.GenerativeModel("gemini-2.5-flash")


class state(TypedDict):
    content : str
    query : str
    line_varification : bool
    resutl : str
    update_query : str 
    delete_backup : str

# def speak(text):
#     engine = pyttsx3.init()   # create a fresh engine
#     engine.setProperty('rate', 150)
#     engine.setProperty('volume', 1.0)
#     engine.say(text)
#     engine.runAndWait()
#     engine.stop()  # ensure engine stops completely


def speak(text):
    """Generate speech and save as MP3 file"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        # Save speech to file
        output_path = r"D:\langGraph\email_agent\response\response.mp3"
        
        # Remove old file if exists
        if os.path.exists(output_path):
            os.remove(output_path)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        engine.stop()
        
        print(f"Speech saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error in speak function: {e}")
        return None



def line_varify(State : state) -> bool:
    if State['line_varification']==True:
        return True
    else:
        return False

def content(state : state)  -> state:
    # print("\n\n\nEnter your question :- ")
    # con = str(input())
    print("I AM IN 'CONTENT'")
    while True:
        content_text = get_text()
        line = delete_Audio()
        if content_text:
            break
        elif content_text == "":
            speak("sorry, i did not get you could you please repeat again")
    return {'content':content_text,'line_varification':line}

def create_query(State : state) -> state:
    print("I AM IN 'CREATE QUERY'")
    print("update querey :- ",State['update_query'])
    if State['update_query']:
        response = model.generate_content(f"""
                                            You are my assistant. 
                                            REMEMBER THESE NAMES for future reference: ['FAISAL','KAIF','SUFFIYAN','SAMEER KHAN'].

                                            This was my previous query:
                                            "{State['query']}"

                                            Now, I want you to update it according to these new instructions if there is any Name then correct it from give refrence:
                                            "{State['update_query']}"

                                            Your task: 
                                            - Rewrite the query in a **simpler and clearer way**.
                                            - Return only **one single improved version** of the query.
                                            - Do not add explanations, only output the updated query.
                                            """).text
    elif State['update_query'] == "":
        known_names = ['Faisal', 'Kaif', 'Suffiyan','Sameer khan']
        response = model.generate_content([
        {
            "role": "user",
            "parts": f"""
                        You are my assistant. 

                        You have a known list of names: {known_names}.
                        If the query contains any of these names but with spelling mistakes or variations, 
                        correct the name to exactly match the one from the list.

                        Here is the user's content:
                        "{State['content']}"

                        Your tasks:
                        1. Correct any name in the query to match the given list.
                        2. Convert the text into a proper, clear question.
                        3. Make sure it explicitly tells the assistant to do the task **by EMAIL**.
                        4. Output must be **only one improved question**, with correct name spellings.
                        5. No explanation, no extra text.
                        """
                                }
                            ]).text
    varificatio = model.generate_content(f'''IF {response} IS EMAIL RELATED QUESTION THEN ONLY RETURN "EMAIL" ELASE "NOT" ''').text
    print(varificatio)
    if varificatio == "EMAIL":
        return {'query':response,'line_varification':True,'update_query':""}
    else:
        return {'query':response,'line_varification':False,'update_query':""}


def varify_query(State : state) -> state:
    print("I AM IN 'VARIFY QUERY'")
    print(f"Do you want to do this {State['query']}\n")
    print("speaking ..........")
    speak(f"Do you want to do this :- {State['query']}")

    start_time = time.time()          # record start
    duration = 1.5 * 60                 # 5 minutes in seconds

    while time.time() - start_time < duration:
        try:
            res = get_text()
            if res:
                delete_Audio()
                break
            elif res =="":
                speak("sorry, i did not get you")
        except:
            pass
        time.sleep(2)
    response = model.generate_content(f'''this is the text "{res}"., 
                                      I NEED IT IN "YES" OR "NO" ONLY. ''').text
        # varificatio = model.generate_content(f'''IF {response} IS EMAIL RELATED QUESTION THEN ONLY RETURN "EMAIL" ELASE "NOT" ''').text
    
    # res  = str(input())
    print("--------------------------------------------This is the response in varify query :-",response)
    if response.lower() == 'yes':
        return {'line_varification':True}
    else:
        speak("OK, i will correct it")
        print("Printing res value :- ",res)
        State['update_query'] = res
        return {'update_query':res,'line_varification':False}
    
def route_varify_query(State: state) -> str:
    return 'yes' if State['line_varification'] else 'no'
    
    
def log_emil(State: state) -> state:
    print("I AM IN 'LOGIN EMAIL'")
    result = "Now logging to email."
    speak(result)

    # dynamically calculate dates
    today = datetime.now().strftime("%Y/%m/%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    last_week_start = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")

    # insert live dates into system prompt examples
    system_prompt = f"""
                            [You are an intelligent email filter extraction agent.

                            Your goal is to analyze the user's natural language query about emails and extract structured filter information.

                            Always return only valid JSON (no explanations, no comments) in this exact schema:
                            {{
                                "after": string | null,
                                "before": string | null,
                                "from": string | null,
                                "limit": integer,
                                "subject": string | null
                            }}

                            ### Rules
                            - Convert relative dates ("today", "yesterday", "last week") into absolute YYYY/MM/DD format.
                            - If no date is mentioned, both after and before = null.
                            - If no limit is mentioned, then limit = null.
                            - Detect sender name after words like "from" or "by".
                            - Detect subject after words like "about", "regarding", or "with subject".
                            - Output must always be valid JSON only.

                            ### Examples

                            User query: "show me emails from John about meeting last week"
                            Output:
                            {{
                                "after": "{last_week_start}",
                                "before": "{today}",
                                "from": "John",
                                "limit": null,
                                "subject": "meeting"
                            }}

                            User query: "give me 5 email which i got today"
                            Output:
                            {{
                                "after": "{today}",
                                "before": "{tomorrow}",
                                "from": null,
                                "limit": 5,
                                "subject": null
                            }}

                            User query: "emails from Alice yesterday"
                            Output:
                            {{
                                "after": "{yesterday}",
                                "before": "{today}",
                                "name": "Alice",
                                "limit": null,
                                "subject": null
                            }}
                            ]
                            """

    # 🧠 Call the model
    response = model.generate_content(
        [
            {
                "role": "user",
                "parts": f"{system_prompt}\n\nUser query: {State['query']}"
            }
        ]
    )

    print("----------------------------------------------------------------")
    print(response.text)
    return {'resutl': response.text, 'line_varification': True}


def fetching(State: state) ->state:
    speak("now fetching the details")

    print("this is state resi;t :----- ",State['resutl'])

    filters = State['resutl']

    # Clean up any markdown-style ```json ... ``` wrapper
    if isinstance(filters, str):
        filters = filters.strip()
        # Remove ```json at start
        if filters.startswith("```json"):
            filters = filters[len("```json"):].strip()
        # Remove ``` at end
        if filters.endswith("```"):
            filters = filters[:-3].strip()
        # Now try to parse
        if filters:
            import json
            filters = json.loads(filters)
        else:
            filters = {}
    elif not isinstance(filters, dict):
        filters = {}

    print("filter is :- ",filters)
    result = filter_emails(filters=filters)

    result_prompt = """You are my smart email assistant. 
                        Your task is to read the extracted email data (like ID, From, Subject, Date, and Body preview) and generate a short, natural spoken summary — as if you are speaking it aloud to the user.

                        Rules:
                        - create it like it will apear human speakable, dont use any sign like(-,'" etc)
                        - Summarize clearly how many emails were found and who sent them.
                        - Mention the date range (earliest and latest email dates).
                        - List each email’s subject with its date.
                        - Use natural, friendly spoken tone — not robotic or overly formal.
                        - Avoid reading the entire body; instead, describe briefly what the messages are about if clear (like “short test messages”).
                        - End with a short concluding line summarizing the sender or purpose.
                        - Do not include raw email IDs or technical details.

                        Example:

                        Input:
                        ID: 199c8404e2ec7fe0
                        From: Sameer Khan <sameerkhan1ssk1@gmail.com>
                        Subject: its 09-oct
                        Date: Thu, 9 Oct 2025 14:44:29 +0530
                        Body preview: hi there this is my first testing of email agent on 09-0ct
                        ...(4 more emails)...

                        Output:
                        “You have received five emails from Sameer Khan this week, between October 7th and 9th. 
                        Here are their subjects: 
                        1 just testing for emailAgent on October 7th, 
                        2 hi there testing final, 
                        3 08-testing, 
                        4 second test  08 oct, and 
                        5 its 09 oct on October 9th. 
                        All of them came from sameerkhan1ssk1@gmail.com.”

                        Now, summarize the given emails in this exact style.
                        """
    response = model.generate_content(
        [
            {
                "role": "user",
                "parts": f"{result_prompt}\n\nUser query: {result}"
            }
        ]
    )

    print("THIS IS RESPOSE OF RESULT :- ",response.text)
    speak(response.text)
    # import time
    # time.wait(5)
    # speak("                                       PLEASE COME AGAIN IF YOU NEED ANY THING ELSE")



def deleteBackups(State: state) ->state:
    folder = r"D:\langGraph\email_agent\audio_backup"
    # folder2 = r"D:\langGraph\email_agent\response"

    # Get all files in the folder
    files = glob.glob(os.path.join(folder, "*"))
    # files2= glob.glob(os.path.join(folder2, "*"))

    for f in files:
        try:
            if os.path.isfile(f):
                os.remove(f)
                print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting {f}: {e}")
    
    # for f in files2:
    #     try:
    #         if os.path.isfile(f):
    #             os.remove(f)
    #             print(f"Deleted: {f}")
    #     except Exception as e:
    #         print(f"Error deleting {f}: {e}")

    print("Backup audio is deleted")
    # print("Response audio is delted")
    return {'delete_backup':"all backup files are detleted"}