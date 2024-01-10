import streamlit as st
import openai
import PyPDF2 as pp
from dotenv import load_dotenv
import os
import pdfkit
import markdown
load_dotenv()

text_to_num = {
    'curt': 150,
    'mitjà': 500,
    'llarg': 1000,
}

# Add to session state
if 'summary_done' not in st.session_state:
    st.session_state.summary_done = False


def read_file(file):
    viewer = pp.PdfReader(file)
    text = ""
    for page_num in range(len(viewer.pages)):
        cur_content = viewer.pages[page_num]
        text += cur_content.extract_text()
    return text


def main():
    st.title("Resumeix el teu PDF amb IA")
    st.markdown("""
    
    """)
    with st.form(key="resumidor"):
        with st.container(border=True):
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                number = st.select_slider("Selecciona la llargada del resum", options=["curt", "mitjà", "llarg"], value="curt")
            with col2:
                lang = st.selectbox("Escull l'idioma", options=['Català', 'Español', 'English'], index=0)
        file = st.file_uploader("Introdueix aquí el fitxer '.pdf' per resumir.", type=[".pdf"])
        button = st.form_submit_button("Resumeix")
        if button:
            st.session_state['summary_done'] = False
    if file is not None:
        with st.spinner("Llegint..."):
            text = read_file(file)
        if not st.session_state['summary_done']:
            with st.spinner("Resumint..."):
                initial_message = {"role": "user", "content": f"""
                Resumeix el text següent de manera que quedin ben clares les idees principals en un màxim de {text_to_num[number]} paraules. 
                Escriu-ho tot en format markdown i utilitza les features de markdown, sobre tot bullet points i negretes. També els èmfasis de paraules ``.
                Fes-ho en l'idioma {lang}.
                
                {text}
                """}
                openai_client = openai.OpenAI(api_key=os.environ["OPENAI_APIKEY"])
                response = openai_client.chat.completions.create(model="gpt-4-1106-preview", messages=[initial_message])
                with open("output.md", "w") as file:
                    file.write(response.choices[0].message.content)
                st.markdown(response.choices[0].message.content)
                st.session_state['summary_done'] = True
            with st.spinner("Generant pdf per descarregar..."):
                markdown_text = response.choices[0].message.content

                # Convert Markdown to HTML
                html_text = markdown.markdown(markdown_text)

                # Create a temporary HTML file
                with open("temp.html", "w") as file:
                    file.write(html_text)

                # Convert HTML to PDF
                pdfkit.from_file("temp.html", "output.pdf")

                # Remove the temporary HTML file
                os.remove("temp.html")

                # Provide the PDF for download
                with open("output.pdf", "rb") as file:
                    st.download_button(label="Download PDF",
                                       data=file,
                                       file_name="summary.pdf",
                                       mime="application/pdf",
                                         )
        else:
            with open("output.md", "r") as file:
                st.markdown(file.read())
            with open("output.pdf", "rb") as file:
                st.download_button(label="Download PDF",
                                   data=file,
                                   file_name="summary.pdf",
                                   mime="application/pdf",
                                   )

if __name__ == '__main__':
    main()