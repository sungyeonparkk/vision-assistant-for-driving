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

openai.api_key = os.environ.get("OPENAI_API_KEY")

MAX_NUM = 2500
INPUT_RANDOM_SAMPLING = False


def parse_question_answer(input_str, video_id):
    question_match = re.search(r"Question:\s*(.*?)\s*\n", input_str)
    answer_match = re.search(r"Answer:\s*((.|\n)*)$", input_str)

    if question_match and answer_match:
        question = question_match.group(1)
        answer = answer_match.group(1)

        result = {"video_id": video_id, "QA": {"q": question, "a": answer}}
        return result
    else:
        return None


if __name__ == "__main__":
    model = "gpt-4"
    CURRENT_DATETIME = datetime.now().strftime("%m-%d_%H%M%S")

    with open("./BDD-captions-reasoning.json", "r") as f:
        inputs = json.load(f)

    # with open("./BDD-instruct-reasoning-09-19_merged.json", "r") as f:
    #     prev_saved = json.load(f)
    #     prev_saved_videos = [x["video_id"] for x in prev_saved]
    prev_saved_videos = []

    system_message = """
    As an AI visual assistant of a driver, you are watching front-view road for around 40 seconds.
    You are given the descriptions of driving situations in chronological order, description of driving scene at the first line, detailed object types and its unique id, bounding boxes of objects (using
    coordinates [bottom left x, top right x, bottom left y, and top right y]), actions of your vehicle.

    And you can infer their relative positions like where other cars and pedestrians exist and are heading to and how close they are from your car from the bounding boxes.
    Also, if there are objects with same id, you can guess where they move toward from your view. Bases on this, you might guess how the driver will act given descriptions related to the traffic situation.
    But, never mention exact coordinates or id of object (ex. car-00096006) and replace it with softer language such as 'moving forward', 'in close proximity', or 'right next to the ego-car'.

    Create a situational reasoning question and an answer between yourself and someone inquiring about the current driving scene. Make sure the response reflect the tone of a AI visual assistant of a driver, actively observing the driving situations and answering questions.
    This Q&A should be ragrding situational Reasoning for traffic understanding.

    Encompass a question which needs complex situational reasoning to be answered, like those discussing events occurred in the road, focusing on important changes or situations that drvier should take care of, 
    or predicting what might happen or how the driver would behave if a given situation went differently, not just asking what happened and what can be seen.

    If a question cannot be answered based on the given descriptions, respond with "It does not present such information" rather than indicating that the information comes
    from text descriptions.

    --
    {}
    --

    In the above description situation, create a QA question (user), answer (car) dataset for complex reasoning between people and cars.
    The format is a conversation with questions and answers alternating as shown below.

    Question: question1
    Answer: answer1
    Question: question2
    Answer: answer2
    …

    Never give time information included in the description.
    Create a natural complex reasoning dataset as if real people were talking!

    Note, indicate your car as ego-car.
    """

    responses = []

    count = 0

    # restart_num = 100

    print(f"Parsing {len(inputs)} inputs")

    with open(
        f"BDD-instruct-reasoning-{CURRENT_DATETIME}.jsonl", "w", encoding="utf-8"
    ) as main_file:
        for index in tqdm(range(len(inputs))):
            if index >= MAX_NUM:
                break
            try:
                count += 1
                # 재시작할 때
                # if count <= restart_num:
                #     continue
                if count % 10 == 0:
                    # 임시 저장본 덮어쓰기
                    with open(f"BDD-instruct_temp.json", "w", encoding="utf-8") as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2)
                    print(f"Saved temporary results at count {count}")

                item = inputs[index]
                if item["video_id"] in prev_saved_videos:
                    continue

                # if INPUT_RANDOM_SAMPLING:
                #     item = random.choice(inputs)

                messages = [
                    {"role": "system", "content": system_message.format(item["desc"])}
                ]

                # uses gpt-3.5-turbo
                chat_completion = openai.ChatCompletion.create(
                    model=model, messages=messages
                )
                result = chat_completion.choices[0].message.content

                for qa in result.split("\n\n"):
                    task = parse_question_answer(qa, item["video_id"])
                    if task is not None:
                        responses.append(task)
                        main_file.write(json.dumps(task) + "\n")

            except Exception as e:
                print(f"Error: {e} {count}")
                with open(f"BDD-instruct_temp.json", "w", encoding="utf-8") as f:
                    json.dump(responses, f, ensure_ascii=False, indent=2)
                time.sleep(1)

    with open(f"BDD-instruct-reasoning.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
