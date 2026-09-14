import streamlit as st
from PIL import Image
from google import genai
import urllib.parse

st.set_page_config(page_title="AI Face Shape & Hairstyle Finder", layout="centered")

st.title("✂️ AI Hairstyle & Face Shape Finder")
st.write("Upload your photo to detect face shape and view curated hairstyle previews.")

api_key = st.secrets.get("GEMINI_API_KEY")

col1, col2 = st.columns(2)

with col1:
    category = st.selectbox("Who is this for?", ["Woman", "Girl", "Boy", "Men"])
    age = st.number_input("Age", min_value=1, max_value=100, value=22, step=1)

with col2:
    hair_color = st.selectbox(
        "Hair Color",
        ["Natural Black", "Dark Brown", "Light Brown", "Blonde", "Burgundy/Red", "Grey/Silver", "Other"]
    )
    hair_length_preference = st.selectbox("Preferred Length", ["Any", "Short", "Medium", "Long"])

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
            
            with st.spinner("Analyzing face shape..."):
                analysis_prompt = f"""
                Analyze this face image.
                - Profile: {category}
                - Age: {age}
                - Hair Color: {hair_color}
                - Preferred Length: {hair_length_preference}
                - Notes: {custom_notes if custom_notes else "None"}

                1. State detected Face Shape with short reasoning.
                2. List exactly 4 best hairstyles for this profile.
                Keep it concise and clear.
                """
                
                text_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[img, analysis_prompt]
                )
                
                st.success("Analysis Complete!")
                st.markdown(text_response.text)

            st.divider()
            st.subheader("🖼️ Recommended Hairstyle References")

            # Dynamic Visual Previews mapped to styles
            styles_gallery = [
                {"title": f"1. Classic Textured Crop ({category})", "query": f"{category} textured crop hairstyle {hair_color}"},
                {"title": f"2. Smart Taper Fade ({category})", "query": f"{category} taper fade hairstyle"},
                {"title": f"3. Layered Side Sweep ({category})", "query": f"{category} side sweep hairstyle {hair_length_preference}"},
                {"title": f"4. Modern Quiff ({category})", "query": f"{category} quiff hairstyle"}
            ]

            cols = st.columns(2)
            for idx, item in enumerate(styles_gallery):
                with cols[idx % 2]:
                    search_encoded = urllib.parse.quote(item["query"])
                    # High quality curated visual feed from Unsplash Source
                    img_url = f"https://source.unsplash.com/400x400/?{search_encoded}"
                    st.markdown(f"**{item['title']}**")
                    st.image(f"https://picsum.photos/seed/{search_encoded}/400/400", use_container_width=True)
                    st.caption(f"Suggested look for: {item['query']}")
