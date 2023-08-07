import json
import os
import openai
import random


if __name__ == "__main__":
    openai.api_key = " "
    model = "gpt-4"

    with open("./BDD-captions.json", "r") as f:
        inputs = json.load(f)

    # Load samples
    with open("./prompt/detailed_decription/caps-01.json", "r") as f:
        sample1 = json.load(f)

    with open("./prompt/detailed_decription/caps-02.json", "r") as f:
        sample2 = json.load(f)

    with open("./prompt/detailed_decription/instructions.json", "r") as f:
        questions = json.load(f)
        questions = questions["instructions"]

    system_message = f"""
    As an AI visual assistant of a driver, you are watching road front-view for around 40 seconds.
    You are given descriptions of driving situarions in chronological order, description of driving scene at the first line, detailing object types and its unique id, bounding boxes of objects(using
    coordinates [bottom left x, top right x, bottom left y, and top right y]), actions of the your vehicle.

    When using the timing description, do not mention it directly with seconds (ex. at 19 seconds, from 00:00 to 00:19) and just utilize it to understand the temporal change of driving scene. 

    And you can infer their relative postions like where other cars and pedestrians exist and are heading to and how close they are from your car from the bounding boxes. 
    Also, if there are objects with same ids, you can guess how they move toward from your view. 

    Base on this, you might guess why the driver acts like given descriptions related to the traffic situation.

    Please use the sequence adverbs "first", "next", "then" and "finally" to describe this driving scene in detail, but don’t mention the specific time. Give as many
    details as possible. Say everything you see. The description should be more than 150 words and less than 200 words. 

    Note, indicate your car as ego-car.
    """

    responses = []

    count = 0

    # restart_num = 6000

    for item in inputs:
        try:
            count += 1
            # 재시작할 때
            # if count <= restart_num:
            #     continue
            if count % 100 == 0:
                # 임시 저장본 덮어쓰기
                with open(f"BDD-X-instruck_temp.json", "w", encoding="utf-8") as f:
                    json.dump(responses, f, ensure_ascii=False, indent=2)
                print(f"Saved temporary results at count {count}")

            question = random.choice(questions)

            messages = [{"role": "system", "content": system_message}]

            messages.append(
                {
                    "role": "user",
                    "content": "\n".join([sample1["desc"], sample1["instruct"]]),
                }
            )
            messages.append({"role": "assistant", "content": sample1["answer"]})
            messages.append(
                {
                    "role": "user",
                    "content": "\n".join([sample2["desc"], sample2["instruct"]]),
                }
            )
            messages.append({"role": "assistant", "content": sample2["answer"]})

            messages.append(
                {"role": "user", "content": "\n".join([item["desc"], question])}
            )

            # uses gpt-3.5-turbo
            chat_completion = openai.ChatCompletion.create(
                model=model, messages=messages
            )
            answer = chat_completion.choices[0].message.content

            task = {"video_id": item["video_id"], "QA": {"q": question, "a": answer}}

            responses.append(task)

        except Exception as e:
            print(f"Error: {e} {count}")
            with open(f"BDD-X-instruck_temp.json", "w", encoding="utf-8") as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)

    with open(f"BDD-X-instruck-3k.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)