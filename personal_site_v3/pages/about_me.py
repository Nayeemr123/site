import streamlit as st
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(layout="centered")

# Function to validate email format
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

# Function to send email
def send_email(name, email, message):
    sender_email = st.secrets['email'] 
    receiver_email = st.secrets['email'] 
    password = st.secrets['e_pass'] 

    subject = f"Contact Form Submitted: {name}" 
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.add_header('Reply-To', email)  # Sets the reply-to field to the user's email

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server: 
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

@st.dialog("Contact Me")
def contact_form():
    with st.form('Contact Form'):
        name = st.text_input('Your Name')
        email = st.text_input('Your Email')
        message = st.text_area('Your Message')
        submit_button = st.form_submit_button('Submit')

        if submit_button:
            if not name or not email or not message:
                st.error('Please fill out all fields.')
            elif not is_valid_email(email.strip()):
                st.error("Please enter a valid email address.")
            else: 
                send_email(name, email, message) #Sends email if all fields are filled out and email is valid
                st.success('Your message has been sent!')

# Custom CSS
custom_css = """
<style>
    body {
        # background-color: #000b1e;  /* Dark navy background color */
    }
    .stApp {
        background-color: #001f3f;  /* Dark navy background color */
    }
    .stButton>button {
        background-color: #7CB9E8;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #7CB9E8;
        color: white;
    }
    # }
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Page layout
col1, col2 = st.columns(2, gap='Small')

with col1:
        st.write("")
        st.image("personal_site_v3/content/profile_pic.png", width=230)

with col2:
    st.title("Nayeem Rahman", anchor=False)
    st.write("Business Analyst | Data Analyst")
    # Contact Form
    if st.button("Contact Me"):
        contact_form()
    # Downloadable Resume
    st.download_button(label="Download Resume", data=open("personal_site_v3/content/Resume Nayeem Rahman.pdf", "rb"), file_name="Nayeem_Rahman_Resume.pdf")

st.write("")
st.write("### Summary")
st.write("I am an expert data and business analyst, specializing in Python, Power BI, and Excel, with a strong focus on building innovative and scalable solutions. My expertise lies in optimizing data pipelines, data visualization, and automation, where I excel at transforming complex ideas into impactful applications. Beyond my technical skills, I am passionate about learning new technologies and business/investing opportunities. I thrive on leveraging technology to solve real-world problems and create value in dynamic fields.")


st.write("### Experience")
st.markdown("""
- Developed and optimized data solutions, including pipeline development, cloud integration, and process automation, to improve data availability and efficiency.
- Created impactful data visualizations and reports, translating complex data into actionable insights for management and stakeholders.
- Streamlined and automated business processes, leveraging data analysis and technical skills to enhance workforce performance.
""")

st.write("### Skills")
st.markdown("""
- Programming Languages: Python (Pandas, NumPy, Matplotlib, Plotly), SQL
- Data Visualization: Power BI, Tableau
- Databases: PostgreSQL, Snowflake, Oracle
- Cloud Platforms: Snowflake, AWS
- Reporting & Automation: Excel (Pivot Tables, XLOOKUP), Python scripting
- Data Workflows: Alteryx
""")
#Media Links
st.write("### Links")
st.markdown("""
- [LinkedIn](https://www.linkedin.com/in/nayeem-rahman532/)
- [GitHub](https://github.com/Nayeemr123)            
""")
