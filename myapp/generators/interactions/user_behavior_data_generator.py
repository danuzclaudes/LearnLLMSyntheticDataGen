from openai import OpenAI

from myapp.utils.file_utils import (data_dir, save_llm_response_data_to_json,
                                    user_behaviors_data_file)


class UserBehaviorDataGen:
    client = OpenAI()

    def generate_synthetic_user_behavior_data(
        self, html_in_str: str, num_of_outputs: int
    ) -> str:

        example_return_json = """
        [
            {
              "user_behavior_id": 1,
              "user_behavior_description": "",
              "user_behavior_explanation": ""
            },
            {
              "user_behavior_id": 2,
              "user_behavior_description": "",
              "user_behavior_explanation": ""
            }
        ]
        """

        few_shot_examples = """
        "User opens the website. They remain idle for 5 seconds, reading the page or glancing at the content. Afterward, they close the browser or navigate away without clicking anything."
        "User opens the website. They begin scrolling slowly after 2 seconds, pausing occasionally as if reading. They stop scrolling at the midway point of the page (the 'About Us' section) and pause for 5 seconds before exiting."
        "User opens the website. They begin scrolling slowly through the hero section and continue scrolling through the 'Listing' section, pausing for 3 seconds and clicks on one image. They then resume scrolling at a steady pace until they reach the footer. They stay on the footer for 7 seconds and exit."
        """

        prompt = f"""
        Given the following HTML structure, understand the topic of the website, and html sections, tags, css.
        You need to generate {num_of_outputs} user behavior patterns for users who are browsing the website.
        
        - Provide a variety of behavior patterns.
        - User can move mouse on the screen.
        - User can scroll up and down between sections.
        - User should not always click an image.
        - User should not always click on the same image.
        - Explain your reasoning and place in the "user_behavior_explanation" field.
        - Explain which tag of HTML element was used in reasoning, to make it traceable for Selenium.
        - Explain which image or url will be clicked by the user and include its css selector.

        HTML structure: {html_in_str}

        Examples of user behavior pattern: {few_shot_examples}
        
        Place the results in the following JSON structure:
        {example_return_json}
        
        Please provide the response without enclosing it in any code blocks.
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
        print(f"Generated user behaviors: {response_data}")
        return response_data


if __name__ == "__main__":
    html_in_str = """
    <html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Luxury Homes in Bellevue, Kirkland, and Redmond</title><meta name="monetag" content="42c82687f7801605e0b2207e69360284"><style>body{margin:0;font-family:Arial,sans-serif;scroll-behavior:smooth}header{position:sticky;top:0;background:rgba(0,0,0,0.8);padding:10px 20px;z-index:1000}nav ul{list-style-type:none;padding:0;display:flex;justify-content:space-around}nav ul li a{color:white;text-decoration:none;padding:10px;transition:color 0.3s}nav ul li a:hover{color:#f0c040}.hero{height:100vh;background-image:url("/static/images/hero-image.jpg");background-size:cover;background-position:center;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;position:relative}.hero::before{content:"";position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5)}.hero h1{z-index:1;font-size:3em;margin:0}.hero p{z-index:1;font-size:1.5em;opacity:0;transform:translateY(20px);animation:slideIn 1s forwards;animation-delay:0.5s}@keyframes slideIn{to{opacity:1;transform:translateY(0)}}.about,.listings,.contact{padding:50px 20px;text-align:center}.about img{width:300px;transition:transform 0.3s}.about img:hover{transform:scale(1.1)}.listing-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}.listing-item{position:relative;overflow:hidden;transition:transform 0.3s}.listing-item img{width:100%;display:block}.listing-item p{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.7);color:white;opacity:0;transition:opacity 0.3s}.listing-item:hover{transform:scale(1.05)}.listing-item:hover p{opacity:1}.contact{background:#f0f0f0}.contact form{display:flex;flex-direction:column;max-width:400px;margin:auto}.contact input,.contact textarea{margin:10px 0;padding:10px;border:1px solid #ccc;border-radius:5px}.contact button{padding:10px;background:#333;color:white;border:none;border-radius:5px;cursor:pointer;transition:background 0.3s}.contact button:hover{background:#555}footer{text-align:center;padding:20px;background:#333;color:white;position:sticky;bottom:0;width:100%}</style></head><body><header><nav><ul><li><a href="#home">Home</a></li><li><a href="#about">About</a></li><li><a href="#listings">Listings</a></li><li><a href="#contact">Contact</a></li></ul></nav></header><section class="hero" id="home"><h1>Luxury Living Awaits</h1><p>Discover your dream home in the heart of Bellevue, Kirkland, and Redmond.</p></section><section class="about" id="about"><h2>About Us</h2><div style="display:flex;justify-content:center;align-items:center;"><img src="/static/images/about-image.jpg" alt="About Image"><div style="margin-left:20px;"><p>We are dedicated to providing the best luxury real estate listings in the area.</p></div></div></section><section class="listings" id="listings"><h2>Listings</h2><div class="listing-grid"><div class="listing-item"><img src="/static/images/listing-image-1.jpg" alt="Listing"><p>List item description here...</p></div><div class="listing-item"><img src="/static/images/listing-image-2.jpg" alt="Listing"><p>List item description here...</p></div><div class="listing-item"><img src="/static/images/listing-image-3.jpg" alt="Listing"><p>List item description here...</p></div><div class="listing-item"><img src="/static/images/listing-image-4.jpg" alt="Listing"><p>List item description here...</p></div></div></section><section class="contact" id="contact"><h2>Contact Us</h2><form onsubmit="return validateForm()"><input type="text" id="name" placeholder="Your Name" required=""><input type="email" id="email" placeholder="Your Email" required=""><textarea id="message" placeholder="Your Message" required=""></textarea><button type="submit">Submit</button></form></section><footer><p>© 2024 ADengBao BRK Homes. All rights reserved.</p></footer><script>function validateForm(){const name=document.getElementById('name').value;const email=document.getElementById('email').value;const message=document.getElementById('message').value;if(name&&email&&message){alert('Form submitted successfully!');return true}alert('Please fill out all fields.');return false}</script></body></html>
    """
    gen = UserBehaviorDataGen()
    data = gen.generate_synthetic_user_behavior_data(
        html_in_str=html_in_str, num_of_outputs=50
    )
    save_llm_response_data_to_json(
        response_data=data, filename=user_behaviors_data_file, data_dir=data_dir
    )
