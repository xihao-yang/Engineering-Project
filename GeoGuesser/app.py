"""
Explainable GeoGuessr AI

A simple zero-shot CLIP demo:
- Upload a street-view or travel image.
- Compare the image against country-specific text prompts.
- Return the Top-3 country predictions with confidence scores.
- Show cautious, human-readable clue explanations for the top prediction.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import gradio as gr
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"

COUNTRIES = [
    "Japan",
    "South Korea",
    "Taiwan",
    "United States",
    "France",
    "Germany",
    "Thailand",
    "Singapore",
]

# Each country gets multiple prompts. Averaging across prompts makes the
# zero-shot prediction a little less dependent on one exact sentence.
PROMPT_TEMPLATES = [
    "a street view photo in {country}",
    "an urban street scene in {country}",
    "a travel photo taken in {country}",
]

# These are not detected objects. They are simple examples of visual patterns
# that may correlate with each country and help explain the model's guess.
COUNTRY_CLUES: Dict[str, List[str]] = {
    "Japan": [
        "Japanese signs",
        "left-side traffic",
        "compact urban streets",
        "vending machines",
    ],
    "South Korea": [
        "Hangul signs",
        "apartment blocks",
        "wide urban roads",
    ],
    "Taiwan": [
        "Chinese signs",
        "scooters",
        "dense urban streets",
    ],
    "United States": [
        "wide roads",
        "road signs",
        "suburban buildings",
    ],
    "France": [
        "European architecture",
        "French signs",
        "narrow streets",
    ],
    "Germany": [
        "European road signs",
        "orderly streets",
        "German language signs",
    ],
    "Thailand": [
        "tropical streets",
        "Thai script signs",
        "motorcycles",
    ],
    "Singapore": [
        "clean urban streets",
        "English signs",
        "high-rise buildings",
    ],
}


def get_device() -> torch.device:
    """Use GPU when available, otherwise run on CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


DEVICE = get_device()

# Loading happens once when the app starts, not every time a user uploads an
# image. The first run may download model files from Hugging Face.
processor = CLIPProcessor.from_pretrained(MODEL_NAME)
model = CLIPModel.from_pretrained(MODEL_NAME).to(DEVICE)
model.eval()


def build_prompts() -> Tuple[List[str], List[str]]:
    """
    Create all text prompts and remember which country each prompt belongs to.

    Returns:
        prompts: flat list of prompt strings
        prompt_countries: country name for each prompt in the same order
    """
    prompts: List[str] = []
    prompt_countries: List[str] = []

    for country in COUNTRIES:
        for template in PROMPT_TEMPLATES:
            prompts.append(template.format(country=country))
            prompt_countries.append(country)

    return prompts, prompt_countries


PROMPTS, PROMPT_COUNTRIES = build_prompts()


@torch.no_grad()
def predict_countries(image: Image.Image) -> List[Tuple[str, float]]:
    """
    Run CLIP zero-shot classification and return all countries with probabilities.

    CLIP compares the uploaded image to text prompts. For each country, this
    function averages the similarity scores across that country's prompts and
    applies softmax to convert the final scores into confidence values.
    """
    rgb_image = image.convert("RGB")

    inputs = processor(
        text=PROMPTS,
        images=rgb_image,
        return_tensors="pt",
        padding=True,
    )
    inputs = {name: value.to(DEVICE) for name, value in inputs.items()}

    outputs = model(**inputs)

    # logits_per_image has shape: [number_of_images, number_of_prompts].
    prompt_scores = outputs.logits_per_image[0]

    country_scores = []
    for country in COUNTRIES:
        prompt_indexes = [
            index
            for index, prompt_country in enumerate(PROMPT_COUNTRIES)
            if prompt_country == country
        ]
        mean_score = prompt_scores[prompt_indexes].mean()
        country_scores.append(mean_score)

    probabilities = F.softmax(torch.stack(country_scores), dim=0)

    ranked_predictions = sorted(
        zip(COUNTRIES, probabilities.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked_predictions


def make_explanation(country: str) -> str:
    """Create a cautious explanation for the highest-ranked prediction."""
    clues = COUNTRY_CLUES.get(country, [])
    clue_text = ", ".join(clues)

    return (
        f"Possible visual clues for this prediction may include {clue_text}. "
        "This demo uses zero-shot CLIP similarity only, so these clues are "
        "general examples rather than confirmed detections in the uploaded image."
    )


def classify_image(image: Optional[Image.Image]):
    """
    Gradio callback for image uploads.

    Returns:
        rows for the Top-3 prediction table and explanation text.
    """
    if image is None:
        return [], "Please upload a street-view or travel image before running the prediction."

    predictions = predict_countries(image)
    top_three = predictions[:3]

    table_rows = [
        [rank, country, f"{probability * 100:.2f}%"]
        for rank, (country, probability) in enumerate(top_three, start=1)
    ]
    explanation = make_explanation(top_three[0][0])

    return table_rows, explanation


with gr.Blocks(title="Explainable GeoGuessr AI") as demo:
    gr.Markdown(
        """
        # Explainable GeoGuessr AI

        Upload a street or travel image. The system predicts the most likely
        country and gives Top-3 results.

        Try images with visible streets, road signs, buildings, storefronts,
        vehicles, or other location-specific context for better results.
        """
    )

    with gr.Row():
        image_input = gr.Image(
            label="Upload street-view or travel image",
            type="pil",
        )

        with gr.Column():
            prediction_output = gr.Dataframe(
                headers=["Rank", "Country", "Confidence"],
                datatype=["number", "str", "str"],
                label="Top-3 Country Predictions",
                interactive=False,
            )
            explanation_output = gr.Textbox(
                label="Explanation",
                lines=5,
                interactive=False,
            )

    predict_button = gr.Button("Predict Country", variant="primary")
    predict_button.click(
        fn=classify_image,
        inputs=image_input,
        outputs=[prediction_output, explanation_output],
    )


if __name__ == "__main__":
    print(f"Starting Explainable GeoGuessr AI on {DEVICE}.")
    demo.launch()
