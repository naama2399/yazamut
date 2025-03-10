import streamlit as st
import base64
import os

# ✅ Set page configuration (MUST be the first Streamlit command)
st.set_page_config(page_title="AI Doula Personalization Questionnaire")

# Path to the new logo image
logo_path = "new logo.png"  # Updated to use PNG

# Function to encode image as Base64
def get_image_base64(image_path):
    """Encodes an image file to a base64 string for display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Display logo at the center
if os.path.exists(logo_path):
    image_base64 = get_image_base64(logo_path)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{image_base64}" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Logo image not found! Please check the file path.")

# Title and Subtitle
st.title("🍼 AI Doula Personalization Questionnaire")
st.write("Helping us create a calming and supportive experience for you during labor.")

def main():
    # General Information
    st.header("1. General Information")
    full_name = st.text_input("Full name (optional)")
    preferred_name = st.text_input("Preferred name/nickname")
    pronouns = st.text_input("Preferred pronouns")
    due_date = st.date_input("Expected due date")

    # Language & Communication Style
    st.header("2. Language & Communication Style")
    st.write("*(You can select multiple options where applicable)*")
    language = st.multiselect("What language(s) would you like AI.doula to use? (Multiple selections allowed)", ["English", "Spanish", "Other"])
    if "Other" in language:
        st.text_input("Please specify other language")

    tone = st.radio("What tone do you find most comforting?",
                    ["Warm and gentle", "Encouraging and empowering", "Calm and neutral", "Other"])
    if tone == "Other":
        st.text_input("Please specify the tone")

    humor = st.radio("Would you like AI.doula to use humor when appropriate?",
                     ["Yes, I appreciate light humor", "A little is fine", "No, I prefer a serious tone"])

    # Support Preferences
    st.header("3. Support Preferences")
    support_preferences = st.multiselect(
        "How do you prefer to receive support? (Multiple selections allowed)",
        [
            "Short affirmations and calming words",
            "Guided breathing exercises",
            "Mindfulness and meditation guidance",
            "Step-by-step explanations",
            "Encouraging messages based on progress",
            "Other",
        ],
    )
    if "Other" in support_preferences:
        st.text_input("Please specify other support preference")

    real_time_support = st.radio("Would you like AI.doula to provide real-time support during contractions?",
                                 ["Yes", "No"])
    st.text_area("Are there any specific affirmations or comforting phrases you'd like to hear?")

    # Sensory Preferences
    st.header("4. Sensory Preferences")
    sensory_preference = st.radio("Do you prefer AI.doula to guide you with:",
                                  ["Spoken words only", "Background calming sounds/music"])
    if sensory_preference == "Background calming sounds/music":
        sound_preference = st.multiselect(
            "If using sounds, what kind do you prefer? (Multiple selections allowed)", 
            [
                "Nature sounds (rain, ocean, etc.)",
                "Soft instrumental music",
                "No sound, just voice",
                "Other",
            ],
        )
        if "Other" in sound_preference:
            st.text_input("Please specify other sound preference")

    # Personalization Based on Past Experiences
    st.header("5. Personalization Based on Past Experiences")
    first_labor = st.radio("Is this your first labor?", ["Yes", "No, I've given birth before"])
    if first_labor == "No, I've given birth before":
        st.text_area("If you've given birth before, is there anything you found helpful last time?")
    st.text_area("Is there anything you'd like to avoid based on past experiences?")
    st.text_area("Do you have any fears or concerns about labor that AI.doula should be aware of?")

    # Partner & Support System
    st.header("6. Partner & Support System")
    include_partner = st.radio(
        "Would you like AI.doula to offer words of encouragement for your birth partner/support person as well?",
        ["Yes", "No"])
    if include_partner == "Yes":
        partner_support = st.multiselect(
            "If yes, how would you like AI.doula to involve them? (Multiple selections allowed)", 
            [
                "Reminders for massage and physical support",
                "Encouraging words for them",
                "Other",
            ],
        )
        if "Other" in partner_support:
            st.text_input("Please specify other support preference for partner")

    # Additional Customization
    st.header("7. Additional Customization")
    st.text_area("Do you have any specific cultural or spiritual preferences AI.doula should be aware of?")
    st.text_area("Any additional preferences or requests?")

    # Submit Button
    if st.button("Submit Questionnaire"):
        st.success("✅ Thank you for completing the questionnaire! Your preferences have been saved.")

if __name__ == "__main__":
    main()
