import os

import boto3


def default_prompts():
    # Return default prompts if the prompt key is not found in DynamoDB
    return {
        "contextPrompt": "Generate a response in a simple list format with hierarchy, "
        "including up to three options. Begin with a headline to set up "
        "the answer. Reiterate the product category mentioned in the inquiry for context.",
        "assistantPrompt": "As an expert language model specialized in the Food & "
        "Beverage sector in the U.S., your knowledge "
        "spans various aspects such as market trends, "
        "consumer preferences, industry regulations, and product innovations. "
        "Your expertise allows you to provide insightful information and "
        "recommendations tailored to the unique challenges and opportunities within "
        "this dynamic sector.",
    }


def get_prompts_from_dynamodb(prompt_key):
    # Retrieve both prompts from DynamoDB using the prompt key
    region_name = os.environ.get("AWS_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    table = dynamodb.Table("bs-olympics-context-prompts")

    response = table.get_item(Key={"sport_key": prompt_key})

    if "Item" in response:
        item = response["Item"]
        return {
            "contextPrompt": item.get(
                "contextPrompt", default_prompts()["contextPrompt"]
            ),
            "assistantPrompt": item.get(
                "assistantPrompt", default_prompts()["assistantPrompt"]
            ),
        }
    else:
        return default_prompts()
