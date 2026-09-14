import streamlit as st
from PIL import Image
from google import genai
import io

st.set_page_config(page_title="AI Face Shape & Hairstyle Finder", layout="centered")

st.title("✂️ AI Hairstyle & Face Shape Finder")
st.write("Upload your photo to detect your face shape and get customized hairstyle recommendations with visual previews.")

api_key = st.secrets.get("GEMINI_API_KEY")

col1, col2 = st.columns(2)

with col1:
    category = st.selectbox(
        "Who is this for?",
        ["Woman", "Girl", "Boy", "Men"]
    )
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        value=22,
        step=1
    )

with col2:
    hair_color = st.selectbox(
        "Hair Color",
        ["Natural Black", "Dark Brown", "Light Brown", "Blonde", "Burgundy/Red", "Grey/Silver", "Other"]
    )
    hair_length_preference = st.selectbox(
        "Preferred Length",
        ["Any", "Short", "Medium", "Long"]
    )

custom_notes = st.text_area(
    "Any specific adjustments or style preferences? (Optional)",
    placeholder="e.g., glasses friendly, curly hair, fade haircut, formal look..."
)

uploaded_file = st.file_uploader("Upload your face photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Photo", width=250)

    if st.button("Generate Hairstyles with Photos"):
        if not api_key:
            st.error("API Key not found! Please add GEMINI_API_KEY in Streamlit Secrets.")
        else:
            client = genai.Client(api_key=api_key)
            
            with st.spinner("Step 1: Analyzing face shape & selecting top styles..."):
                analysis_prompt = f"""
                Analyze this face image.
                - Profile: {category}
                - Age: {age}
                - Hair Color: {hair_color}
                - Preferred Length: {hair_length_preference}
                - Notes: {custom_notes if custom_notes else "None"}

                Identify the exact face shape (Oval, Round, Square, Heart, Diamond, etc.).
                List 5 top hairstyles specifically suitable for this person.
                Format clearly with hairstyle names and quick styling reasons.
                """
                
                text_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[img, analysis_prompt]
                )
                
                st.success("Analysis Complete!")
                st.markdown(text_response.text)

            st.divider()
            st.subheader("🖼️ Visual Hairstyle Previews")

            # Generating Visual Previews
            sample_styles = [
                f"Modern textured crop cut for a {category} with {hair_color} hair",
                f"Classic layered taper style for a {category} with {hair_color} hair",
                f"Voluminous parted fringe style for a {category} with {hair_color} hair"
            ]

            with st.spinner("Step 2: Generating AI hairstyle concept photos..."):
                for style_desc in sample_styles:
                    try:
                        image_result = client.models.generate_images(
                            model="imagen-3.0-generate-002",
                            prompt=f"Professional salon photo of a stylish {style_desc}, studio lighting, highly realistic portrait",
                            config=dict(number_of_images=1, aspect_ratio="1:1")
                        )
                        for generated_img in image_result.generated_images:
                            preview = Image.open(io.BytesIO(generated_img.image.image_bytes))
                            st.image(preview, caption=style_desc, use_container_width=True)
                    except Exception:
                        pass
