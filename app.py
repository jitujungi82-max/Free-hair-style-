import streamlit as st
from PIL import Image
from google import genai

st.set_page_config(page_title="AI Face Shape & Hairstyle Finder", layout="centered")

st.title("✂️ AI Hairstyle & Face Shape Finder")
st.write("Upload your photo, select your profile details, and add any custom preferences to get 10 tailored hairstyles.")

# Fetch API Key from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Selection Controls
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

# User Custom Modifications / Instructions Box
custom_notes = st.text_area(
    "Any specific adjustments or style preferences? (Optional)",
    placeholder="e.g., I wear glasses, need low-maintenance style, want beard match, curly hair only, etc."
)

# File Uploader
uploaded_file = st.file_uploader("Upload your face photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Photo", width=250)

    if st.button("Generate 10 Hairstyles"):
        if not api_key:
            st.error("API Key not found! Please add GEMINI_API_KEY in Streamlit Secrets.")
        else:
            with st.spinner("AI is analyzing your face and generating 10 personalized styles..."):
                client = genai.Client(api_key=api_key)

                prompt = f"""
                You are a master hair stylist and salon consultant.
                Analyze the uploaded face photo carefully considering these user details:
                - Profile: {category}
                - Age: {age} years old
                - Hair Color: {hair_color}
                - Preferred Length: {hair_length_preference}
                - Custom User Requests/Adjustments: {custom_notes if custom_notes else "None provided"}

                Provide a structured report including:
                1. **Detected Face Shape** (e.g., Oval, Round, Square, Heart, Diamond, Oblong) with a 1-line justification.
                2. **Top 10 Recommended Hairstyles**:
                   Provide exactly 10 distinct, numbered hairstyle recommendations tailored specifically for this person's face shape, age ({age}), category ({category}), and custom preferences.
                   For each style, include:
                   - **Name of the Hairstyle**
                   - **Why it fits their face shape & features**
                   - **Quick Styling Tip**
                3. **Maintenance & Care Tip**: 1-2 practical tips matching their selected hair color and length.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[img, prompt]
                )

                st.success("Analysis Complete!")
                st.markdown(response.text)
