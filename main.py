import streamlit as st
import openai
import PyPDF2 as pp
from dotenv import load_dotenv
import os
import pypandoc
load_dotenv()

text_to_num = {
    'curt': 250,
    'mitjà': 1000,
    'llarg': 2000,
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
                Resumeix el text següent en l'idioma {lang} i en més o menys {text_to_num[number]} paraules. Desenvolupa bé cada idea principal.
                L'objectiu és poder entendre el text original sense haver de llegir-lo tot. 
                Si hi ha conceptes clau, explica'ls bé.
                Escriu-ho tot en format markdown i utilitza les features de markdown perquè s'entengui bé.
                Fes-ho en l'idioma {lang}.
                El text està entre els guionets (---).
                ---
                {text}
                ---
                """}
                openai_client = openai.OpenAI(api_key=os.environ["OPENAI_APIKEY"])
                response = openai_client.chat.completions.create(model="gpt-4-1106-preview", messages=[initial_message])
                with open("output.md", "w") as file:
                    file.write(response.choices[0].message.content)
                st.markdown(response.choices[0].message.content)
                st.session_state['summary_done'] = True
            with st.spinner("Generant pdf per descarregar..."):
                markdown_text = response.choices[0].message.content

                # Convert Markdown to pdf
                pypandoc.convert_text(markdown_text, 'pdf', format='md', outputfile="output.pdf", extra_args=['--pdf-engine=xelatex'])

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
                st.download_button(label="Descarrega el PDF",
                                   data=file,
                                   file_name="summary.pdf",
                                   mime="application/pdf",
                                   )

if __name__ == '__main__':
    main()