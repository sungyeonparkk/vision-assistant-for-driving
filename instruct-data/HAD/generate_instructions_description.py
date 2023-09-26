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
        inputs = [x for x in inputs if x["split"] == "desc"]

    # with open("./HAD-instruct-reasoning-230924.json", "r") as f:
    #     prev_saved = json.load(f)
    #     prev_saved_videos = [x["video_id"] for x in prev_saved]
    prev_saved_videos = []

    system_message = """
    As an AI visual assistant of a driver, you are watching front-view road for around 20 seconds.
    You are given the summarization of road events and manuever of your ego-car during 20 seconds and some detailed information, which inlcudes "[attention]" you may take care of while driving,
    "[cause]" that makes you do [sitmulus-driven] behavior, "[goal-oriented]" that you do with a purpose of going somewhere or else, "[stimulus-driven]" behavior that reaction to some changes on road or traffic,
    "[Steering angles]" that is steering angle of ego-car at every second, and "[Velocities]" that is velocity of ego-car at every second.

    Create a detailed description based on given information of current driving scene. 
    Say everything you see, but do not inlcude what you did not see. The description should be less than 150 words.

    When you describe the scene, never mention given description directly, such as veclocity and steering angle.
    Alos, never give time information included in the description.

    Never mention these words.
    (velocity, steering angel, goal-oriented, stimulus-driven, AI, assistant)

    Note, indicate your car as ego-car.

    --
    {}
    --

    In the above driving situation, create a proper question to describe the current scene and proper anwer for it.
    The format should be 

    Question: your question
    Answer: your answer
    """

    responses = []

    count = 0

    # restart_num = 100

    print(f"Parsing {len(inputs)} inputs")

    with open(
        f"HAD-instruct-description-{CURRENT_DATETIME}.jsonl", "w", encoding="utf-8"
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

    with open(f"HAD-instruct-description.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
