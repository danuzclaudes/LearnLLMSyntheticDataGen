from openai import OpenAI

from myapp.generators.webapp.website_generators import llm_website_gen_prompt

client = OpenAI()


if __name__ == "__main__":

    # Generate random website content using OpenAI's GPT-4 or GPT-3.5 (latest models)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Generate a random website content about cars and vehicles.",
            },
        ],
        max_tokens=150,
        temperature=0.7,  # Control creativity (higher = more creative)
    )
    print(completion.choices[0].message.content.strip())

    # Generate random image
    response = client.images.generate(
        prompt="A modern stylish car showroom with luxury cars displayed",
        n=1,
        size="1024x1024",
    )
    image_url = response.data[0].url
    print(image_url)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"{llm_website_gen_prompt}",
            },
        ],
        # max_tokens=150,
        temperature=0.7,  # Control creativity (higher = more creative)
    )
    print(completion.choices[0].message.content.strip())
