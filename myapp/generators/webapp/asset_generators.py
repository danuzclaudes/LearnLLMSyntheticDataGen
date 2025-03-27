import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal

from openai import OpenAI

from myapp.utils.file_utils import download_and_save_image

# hero_image_gen_prompt = """
# Generate an image of a modern, stylish car showroom featuring luxury cars.
# The cars in the showroom should look brand new and without any visible damage.
#
# The overall scene should evoke a sense of luxury, professionalism, and high-end automotive design.
# """
#
# about_image_gen_prompt = """
# Generate an image of a professional, modern car dealership office.
#
# The office should be clean, minimalist, and well-lit with a modern design.
# It should include elements such as sleek furniture, a reception desk, and large windows allowing natural light.
# The space should feel welcoming, professional, sophisticated, with neutral tones like white, gray, and wood accents.
# The image should evoke a sense of trust and professionalism, suitable for a car purchasing and selling business.
# """
#
#
# car_image_gen_prompt = """
# Generate a car image.
#
# The cars should look modern, stylish, luxury, compatible with the car showroom.
# """

hero_image_gen_prompt = """
Create a sophisticated, modern living room with high-end décor and furniture that looks realistic and lifelike.
All decors and furniture must not look artificial.
Incorporate subtle elements that reflect real estate expertise, like architectural models,
high-quality property brochures, or advanced technology, seamlessly integrated into the design.
The color palette should be refined and upscale, featuring greys, gold accents, and soft whites.

The image should be designed as a full-page background for a real estate website
Tne image must provide the impression of a high-end living space.
All elements, from the furnishings to the décor, must not look artificial, must be realistic, and high-resolution.
"""

about_image_gen_prompt = """
Create an elegant and sophisticated image that conveys the essence of a luxury real estate business
specializing in high-end properties.
The scene should feature an opulent, contemporary office or meeting room with sleek, modern furniture and rich décor.
There should be subtle elements that reflect real estate expertise, such as architectural models, property brochures,
or high-end technology.
The color palette should be refined, with shades of grey, gold, and white to evoke professionalism and trust.
The overall atmosphere should be welcoming, yet luxurious, highlighting a premium, exclusive service
for high-net-worth clients.
The image should be suitable for use as a background on the About page of a luxury real estate website.
"""


listing_item_image_gen_prompt = """
Generate an image of a newly designed, modern, and stylish luxury house that is still under construction.
The design should reflect high-end, contemporary architecture with sleek lines and innovative features,
but not overly extravagant – suited for upper-middle-class millionaires, not billionaires.
The house should have a technical, architectural look, showcasing advanced design elements like large windows,
open spaces, and functional layouts, but still feel grounded in reality.
The exterior should feature a blend of modern materials like wood, glass, and stone, with a inviting color palette.
The design should look both creative and realistic, reflecting a home that feels attainable yet luxurious.

"""


@dataclass
class Assets:
    hero_image_path: str = None
    about_image_path: str = None
    listing_image_paths: List = field(default_factory=list)


class AssetGenerator:
    client = OpenAI()

    def generate_asset_images(self, static_folder: str) -> Assets:
        hero_image_path = self._generate_and_save_image_if_not_exists(
            static_folder=static_folder,
            image_name="hero-image.jpg",
            image_size="1024x1024",
            num_of_images=1,
            image_gen_prompt=hero_image_gen_prompt,
        )
        about_image_path = self._generate_and_save_image_if_not_exists(
            static_folder=static_folder,
            image_name="about-image.jpg",
            image_size="1024x1024",
            num_of_images=1,
            image_gen_prompt=about_image_gen_prompt,
        )

        listing_image_paths = self._generate_listing_items_images(
            static_folder=static_folder,
        )

        return Assets(
            hero_image_path=hero_image_path,
            about_image_path=about_image_path,
            listing_image_paths=listing_image_paths,
        )

    def _generate_and_save_image_if_not_exists(
        self,
        static_folder: str,
        image_name: str,
        image_size: Literal[
            "256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"
        ],
        num_of_images: int,
        image_gen_prompt: str,
    ):
        image_dir = Path(static_folder) / "images"
        image_file = image_dir / image_name

        # If the image already exists, return the path and skip generation
        if os.path.exists(image_file):
            print(
                f"Image {image_name} already exists at path={image_file}, skipping..."
            )
            return f"images/{image_name}"

        # Generate image using OpenAI's DALL·E
        print(f"Generating image at path={image_file}...")
        response = self.client.images.generate(
            prompt=image_gen_prompt,
            n=num_of_images,
            size=image_size,
        )
        image_url = response.data[0].url

        # Download and save the generated image
        download_and_save_image(image_url=image_url, save_path=image_file)

        print(f"Successfully generated image and saved to {image_file}")
        return f"images/{image_name}"

    def _generate_listing_items_images(self, static_folder: str) -> List[str]:
        listing_image_paths = []
        for i in range(1, 5):
            listing_image_name = f"listing-image-{i}.jpg"
            listing_image_path = f"images/{listing_image_name}"

            # Call the method to generate and save the image for each listing item
            self._generate_and_save_image_if_not_exists(
                static_folder=static_folder,
                image_name=listing_image_name,
                image_size="1024x1024",
                num_of_images=1,
                image_gen_prompt=listing_item_image_gen_prompt,
            )

            # Append the image path to the list
            listing_image_paths.append(listing_image_path)
        return listing_image_paths
