import json

from openai import OpenAI

from myapp.utils.batch_utils import BatchProcessor
from myapp.utils.file_utils import (data_dir, load_json_array_data,
                                    load_llm_response_data_as_json,
                                    save_llm_response_data_to_json,
                                    user_behaviors_data_file,
                                    user_interactions_data_file,
                                    user_profiles_data_file)
from myapp.utils.prompt_utils import website_business

TOTAL_NUM_BATCHES = 100


class UserInteractionsDataGen:
    client = OpenAI()

    def generate_synthetic_user_interactions_data(
        self,
        num_of_outputs: int,
        user_behaviors_data: list[dict],
        user_profiles_data: list[dict],
    ) -> str:

        example_return_json = """
        [
            {
              "interaction_id": 1,
              "user_behavior_id": 1,
              "user_profile_id": 1,
              "user_behavior_description": "",
              "user_behavior_explanation": "",
              "user_profile_description": "",
              "region": "",
              "user_agent": "",
              "user_interaction_explanation": ""
            },
            {
              "interaction_id": 2,
              "user_behavior_id": 1,
              "user_profile_id": 1,
              "user_behavior_description": "",
              "user_behavior_explanation": "",
              "user_profile_description": "",
              "region": "",
              "user_agent": "",
              "user_interaction_explanation": ""
            }
        ]
        """

        prompt = f"""
        You are given two json arrays.
        user_behaviors_data: user behavior patterns for users who are browsing the website.
        user_profiles_data: contain user profiles who are simulated to browse a website about {website_business}.
        
        Generate {num_of_outputs} user interactions data.
        
        For each user interaction data,
        - Pick one array item from user_behaviors_data and one array item from user_profiles_data.
        - The picked user behavior and user profile must make sense, simulating real human behavior.
        - Explain your reasoning and place in the "user_interaction_explanation" field.
        - For the field user_behavior_description, must use the same value from the picked user_behaviors_data item.
        - For the field user_behavior_explanation, must use the same value from the picked user_behaviors_data item.
        - For the field user_profile_description, must use the same value from the picked user_profiles_data.
        - For the field region, must use the same value from the picked user_profiles_data.
        - For the field user_agent, must use the same value from the picked user_profiles_data.
        
        user_behaviors_data={user_behaviors_data}
        user_profiles_data={user_profiles_data}
        
        Place the results in the following JSON structure: {example_return_json}
        
        Please provide the response without enclosing it in any code blocks.
        The JSON should be fully formed and complete, with no ... or missing values, or comments.
        """

        # print(prompt)

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        response_data = completion.choices[0].message.content.strip()
        return response_data

    def generate_batch(
        self,
        batch_index,
        num_of_outputs_per_batch,
        user_behaviors_data,
        user_profiles_data,
    ):
        print(f"Processing batch {batch_index + 1}...\n")
        response_data = self.generate_synthetic_user_interactions_data(
            num_of_outputs=num_of_outputs_per_batch,
            user_behaviors_data=user_behaviors_data,
            user_profiles_data=user_profiles_data,
        )
        response_data_in_json = load_llm_response_data_as_json(
            response_data=response_data
        )
        print(
            f"Batch {batch_index + 1} completed with {len(response_data_in_json)} items."
        )
        return response_data_in_json

    def generate_user_interactions_in_batches(
        self, num_of_outputs_per_batch: int, num_of_batches: int
    ) -> str:
        user_behaviors_data = load_json_array_data(
            data_dir=data_dir, data_file_name=user_behaviors_data_file
        )
        user_profiles_data = load_json_array_data(
            data_dir=data_dir, data_file_name=user_profiles_data_file
        )

        processor = BatchProcessor()
        response_data_in_batches = processor.process_batches(
            num_of_batches=num_of_batches,
            batch_function=self.generate_batch,
            num_of_outputs_per_batch=num_of_outputs_per_batch,
            user_behaviors_data=user_behaviors_data,
            user_profiles_data=user_profiles_data,
        )

        # for batch_index in range(num_of_batches):
        #     print(f"Processing batch {batch_index + 1}/{num_of_batches}...")
        #     response_data = self.generate_synthetic_user_interactions_data(
        #         num_of_outputs=num_of_outputs_per_batch,
        #         user_behaviors_data=user_behaviors_data,
        #         user_profiles_data=user_profiles_data,
        #     )
        #
        #     response_data_in_json = load_llm_response_data_as_json(
        #         response_data=response_data
        #     )
        #     response_data_in_batches.extend(response_data_in_json)
        #     # Rate limiting (adjust as needed)
        #     time.sleep(1)  # 1 second delay to prevent overwhelming the LLM

        for index, interaction_data in enumerate(response_data_in_batches):
            if "interaction_id" in interaction_data:
                interaction_data["interaction_id"] = index + 1
            else:
                raise RuntimeError(
                    f"interaction_data has no interaction_id: {interaction_data}"
                )
        print(f"Batch processing complete: {response_data_in_batches}")
        return json.dumps(response_data_in_batches)


if __name__ == "__main__":
    gen = UserInteractionsDataGen()
    # data = gen.generate_synthetic_user_interactions_data(num_of_outputs=1)
    batch_data = gen.generate_user_interactions_in_batches(
        num_of_outputs_per_batch=5, num_of_batches=TOTAL_NUM_BATCHES
    )
    save_llm_response_data_to_json(
        response_data=batch_data,
        filename=user_interactions_data_file,
        data_dir=data_dir,
    )
