import json
import os
import openai
import random
from tqdm import tqdm
from datetime import datetime
import time
import re

from dotenv import load_dotenv

load_dotenv()

openai.api_key = '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'

MAX_NUM = 2000
INPUT_RANDOM_SAMPLING = True

def parse_question_answer(input_str):
    question_match = re.search(r"Question:\s*(.*?)\s*\n", input_str)
    answer_match = re.search(r"Answer:\s*((.|\n)*)$", input_str)

    if question_match and answer_match:
        question = question_match.group(1)
        answer = answer_match.group(1)
        
        result = {
            "QA": {
                "q": question,
                "a": answer
            }
        }
        return result
    else:
        return None

if __name__ == "__main__":
    model = "gpt-4"
    CURRENT_DATETIME = datetime.now().strftime("%m-%d_%H%M%S")

    with open("./BDD-captions.json", "r") as f:
        inputs = json.load(f)

    # Load samples
    with open("../prompt/complex_reasoning/caps-01.json", "r") as f:
        sample1 = json.load(f)

    with open("../prompt/complex_reasoning/caps-02.json", "r") as f:
        sample2 = json.load(f)

    with open("../prompt/complex_reasoning/instructions.json", "r") as f:
        questions = json.load(f)
        questions = questions["instructions"]

    system_message = f"""
    As an AI visual assistant of a driver, you are watching front-view road for around 40 seconds.
    You are given the descriptions of driving situations in chronological order, description of driving scene at the first line, detailed object types and its unique id, bounding boxes of objects (using
    coordinates [bottom left x, top right x, bottom left y, and top right y]), actions of your vehicle.

    When using the timing description, do not mention it directly with seconds (ex. at 19 seconds, from 00:00 to 00:19) and just utilize it to understand the temporal change of driving scene.

    And you can infer their relative positions like where other cars and pedestrians exist and are heading to and how close they are from your car from the bounding boxes.
    Also, if there are objects with same id, you can guess where they move toward from your view.

    Bases on this, you might guess how the driver will act given descriptions related to the traffic situation.

    Create a question and an answer between yourself and someone inquiring about the video. Make sure the response reflect the tone of a AI visual assistant of a driver, actively observing the video of  driving situations and answering questions.


    Encompass a question which needs complex reasoning to be answered, like those asking about
    the background knowledge of objects or actions in the video, discussing events occurring
    in the video, delving into counterfactual topics, seeking explanations for characters’
    emotions or behaviors based on their experiences in the video, or predicting how the video’s
    story or scene will progress.

    You may incorporate questions that address the visual content of the video, such as object types,
    attributes, object counting, actions, locations, relative positions between objects, and
    changes in object actions or locations over time, as well as object interactions.

    Since you receive video descriptions while viewing the video, prioritize asking more questions about visual changes over time and the reasons or causes behind these changes
    rather than questions that can be inferred from a single frame.
    You should ask question which can be answered using multiple information of the video and demand complex reasoning ability.

    Remember not to inquire about uncertain details. When answering a complex question,
    provide thorough answers, **incorporating detailed examples or steps of reasoning** to make
    the content more persuasive and well-structured. Use multiple paragraphs if necessary. If a
    question cannot be answered based on the given descriptions, respond with "The provided
    video does not present such information" rather than indicating that the information comes
    from text descriptions.

    You should output question you made in this format "Question: ".
    You should output answer you made in this format "Answer: ".

    Note, indicate your car as ego-car.
    """

    responses = []

    count = 0

    # restart_num = 6000
    
    print(f"Parsing {len(inputs)} inputs")

    with open(f"BDD-instruct-3k-{CURRENT_DATETIME}.jsonl", "w", encoding="utf-8") as main_file:
        for index in tqdm(range(len(inputs))):
            if index >= MAX_NUM:
                break
            try:
                count += 1
                # 재시작할 때
                # if count <= restart_num:
                #     continue
                if count % 100 == 0:
                    # 임시 저장본 덮어쓰기
                    with open(f"BDD-instruct_temp.json", "w", encoding="utf-8") as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2)
                    print(f"Saved temporary results at count {count}")

                item = inputs[index]
                if INPUT_RANDOM_SAMPLING:
                    item = random.choice(inputs)
                
                question = random.choice(questions)

                messages = [{"role": "system", "content": system_message}]

                messages.append(
                    {
                        "role": "user",
                        "content": sample1["desc"]
                    }
                )
                messages.append(
                    {
                        "role": "assistant", 
                        "content": f"question: {sample1['instruct']}\nanswer: {sample1['answer']}"
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": sample2["desc"]
                    }
                )
                messages.append(
                    {
                        "role": "assistant", 
                        "content": f"question: {sample2['instruct']}\nanswer: {sample2['answer']}"
                    }
                )

                # uses gpt-3.5-turbo
                chat_completion = openai.ChatCompletion.create(
                    model=model, messages=messages
                )
                result = chat_completion.choices[0].message.content
                task = parse_question_answer(result)
                if task is not None:
                    responses.append(task)

            except Exception as e:
                print(f"Error: {e} {count}")
                with open(f"BDD-instruct_temp.json", "w", encoding="utf-8") as f:
                    json.dump(responses, f, ensure_ascii=False, indent=2)
                time.sleep(1)
            else:
                main_file.write(json.dumps(task) + '\n')

    with open(f"BDD-instruct-3k.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
