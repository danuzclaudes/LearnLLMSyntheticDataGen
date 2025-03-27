import os
from dataclasses import dataclass

from openai import OpenAI

from myapp.utils.prompt_utils import website_business

index_file = "index.html"


llm_website_gen_prompt = f"""
Create a single-page website for {website_business}.
The website should be modern, visually appealing, and responsive.
The design should include all HTML, CSS, and JavaScript in a single file.
Include the following sections and features:

Header/Nav Bar:
A sticky navigation bar at the top of the page with links to Home, About, Details, and Contact sections.
Smooth scroll functionality should allow users to jump between sections.

Hero Section:
The hero section should feature a full-screen background image with a dark overlay for better text visibility.
Ensure the background image is set to cover the entire screen without breaking its proportions.
The background image path should be dynamically passed via Flask as hero_image_path,
and the image should be referenced in the CSS using Flask's url_for function, like so:
background-image: url("{{{{ url_for('static', filename=hero_image_path) }}}}");.
The section must include a large, bold title.
The section must also have a brief introduction with a slide-in effect from the bottom.
The introduction should appear smoothly from the center
The introduction must be put below title with appropriate spacing.
All texts should be readable with a contrasting overlay background.
Ensure that the Hero section covers the entire viewport with no overflow.

About Section:
A section with a short biography of the business owner or company.
Display a photo on the left, with a zoom-in effect on hover.
The image should be referenced using Flask's url_for function like so:
<img src="{{{{ url_for('static', filename=about_image_path) }}}}" alt="About Image">.
Text about the company or owner should be on the right.

Listing Section:
Create a grid layout displaying 3-6 listings.
Each model should have an image, title, and description that appears on hover.
The image source for each listing should be dynamically passed via Flask, and referenced in HTML using url_for:
<div class="details-section">
    <div class="listing-grid">
        {{% for listing_image_path in listing_image_paths %}}
            <div class="listing-item">
                <img src="{{{{ url_for('static', filename=listing_image_path) }}}}" alt="Listing">
                <p>List item description here...</p>
            </div>
        {{% endfor %}}
    </div>
</div>

Contact Section:
A simple contact form with fields for Name, Email, and Message, along with a Submit button.
The form should include client-side validation to ensure all fields are filled out before submission.

Footer:
A sticky footer with copyright information.

CSS Design:
Use modern CSS techniques like Flexbox or Grid for responsiveness.
The design should adapt to different screen sizes, including mobile and tablet.
Choose a clean, minimalist color scheme with two or three complementary colors for a professional look.

Animations:
Add smooth animations such as fade-ins, slide-ins, or scaling effects for sections as users scroll.
Use a lightweight JavaScript library like AOS or native JavaScript with IntersectionObserver to trigger animations.

The website should have smooth scrolling for navigation and subtle interaction effects like button hover transitions.
It must be lightweight, load quickly, and be fully responsive across all devices.

Double ensure the website must be modern, visually appealing, and responsive.
Only return pure html code, no explanations, no summaries, no code formatting.
"""


@dataclass
class WebsiteGenerator:
    client = OpenAI()

    def generate_index_html_if_not_exists(self, root_path: str):
        index_path = os.path.join(root_path, "templates")
        index_html = os.path.join(index_path, "index.html")

        if os.path.exists(index_html):
            print(f"{index_html} already exists. Skipping HTML generation...")
            return

        print(f"Generating html {index_html}...")
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a web UI designer."},
                {
                    "role": "user",
                    "content": f"{llm_website_gen_prompt}",
                },
            ],
            temperature=0.7,  # Control creativity (higher = more creative)
        )

        html_code = completion.choices[0].message.content.strip()
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_html, "w") as file:
            file.write(html_code)
        print(f"HTML code has been saved to {index_path}")
