from openai import OpenAI

from myapp.utils.file_utils import (data_dir, save_llm_response_data_to_json,
                                    user_profiles_data_file)
from myapp.utils.prompt_utils import website_business


class UserProfileDataGen:
    client = OpenAI()

    def generate_synthetic_user_profile_data(self, num_of_outputs: int):
        possible_regions = [
            "Seattle",
            "Bellevue",
            "Redmond",
            "Kirkland",
            "Cupertino",
            "Los Angeles",
            "Bay Area",
            "Shanghai",
            "Beijing",
            "Boston",
            "Vancouver",
            "New York",
        ]
        example_return_json = """
        [
            {
              "user_profile_id": 1,
              "user_profile_description": "",
              "region": "",
              "user_agent": ""
            },
            {
              "user_profile_id": 2,
              "user_profile_description": "",
              "region": "",
              "user_agent": ""
            }
        ]
        """
        prompt = f"""
        You need to generate {num_of_outputs} user profiles to simulate users.
        The users will browse a website about {website_business}.
        
        Place the results in the following JSON structure: {example_return_json}
        
        - For the field region, pick one from {possible_regions}.
        - For the field user_agent, specifies the browser, operating system, and other relevant details.
        - Please provide the response without enclosing it in any code blocks.
        - Please provide the output as a valid JSON array with no placeholders or omissions.
        - The JSON should be fully formed and complete, with no ... or missing values, or comments.
        """

        print(prompt)
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"{prompt}",
                },
            ],
            temperature=0.9,  # Control creativity (higher = more creative)
        )
        response_data = completion.choices[0].message.content.strip()
        print(f"Generated user behaviors:\n{response_data}")
        return response_data


if __name__ == "__main__":
    gen = UserProfileDataGen()
    data = gen.generate_synthetic_user_profile_data(num_of_outputs=150)
    save_llm_response_data_to_json(
        response_data=data, filename=user_profiles_data_file, data_dir=data_dir
    )
