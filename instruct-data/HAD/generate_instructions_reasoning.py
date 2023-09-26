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

openai.api_key = ""

# MAX_NUM = 2500
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

    with open("./HAD-captions.json", "r") as f:
        inputs = json.load(f)

    with open("./HAD-instruct-reasoning-230924.json", "r") as f:
        prev_saved = json.load(f)
        prev_saved_videos = [x["video_id"] for x in prev_saved]

    system_message = """
    As an AI visual assistant of a driver, you are watching front-view road for around 20 seconds.
    You are given the summarization of road events and manuever of your ego-car during 20 seconds and some detailed information, which inlcudes "[attention]" you may take care of while driving,
    "[cause]" that makes you do [sitmulus-driven] behavior, "[goal-oriented]" that you do with a purpose of going somewhere or else, "[stimulus-driven]" behavior that reaction to some changes on road or traffic,
    "[Steering angles]" that is steering angle of ego-car at every second, and "[Velocities]" that is velocity of ego-car at every second.

    Create a situational reasoning question and an answer between yourself and someone inquiring about the current driving scene. Make sure the response reflect the tone of a AI visual assistant of a driver, actively observing the driving situations and answering questions.
    This Q&A should be regarding situational Reasoning for traffic understanding.

    Encompass a question which needs complex situational reasoning to be answered, like those discussing events occurred in the road, focusing on important changes or situations that drvier should take care of, 
    or predicting what might happen or how the driver would behave if a given situation went differently, not just asking what happened and what can be seen.

    When you answer the question, never mention given description directly, such as veclocity and steering angle.
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
        f"HAD-instruct-reasoning-{CURRENT_DATETIME}.jsonl", "w", encoding="utf-8"
    ) as main_file:
        for index in tqdm(range(len(inputs))):
            try:
                count += 1
                # 재시작할 때
                # if count <= restart_num:
                #     continue
                if count % 10 == 0:
                    # 임시 저장본 덮어쓰기
                    with open(f"HAD-instruct_temp.json", "w", encoding="utf-8") as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2)
                    print(f"Saved temporary results at count {count}")

                item = inputs[index]
                if item["video_id"] in prev_saved_videos:
                    continue
                if item["split"] in ["conv", "desc"]:
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
                with open(f"HAD-instruct_temp.json", "w", encoding="utf-8") as f:
                    json.dump(responses, f, ensure_ascii=False, indent=2)
                time.sleep(1)

    with open(f"HAD-instruct-reasoning.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
