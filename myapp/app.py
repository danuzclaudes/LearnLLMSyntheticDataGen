from flask import Flask, render_template

from myapp.generators.webapp.asset_generators import AssetGenerator, Assets
from myapp.generators.webapp.website_generators import WebsiteGenerator

app = Flask(__name__)
website_generator = WebsiteGenerator()
asset_generator = AssetGenerator()


@app.route("/")
def home():
    website_generator.generate_index_html_if_not_exists(root_path=app.root_path)

    assets: Assets = asset_generator.generate_asset_images(
        static_folder=app.static_folder
    )

    return render_template(
        "index.html",
        hero_image_path=assets.hero_image_path,
        about_image_path=assets.about_image_path,
        listing_image_paths=assets.listing_image_paths,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
