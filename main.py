import streamlit as st
import openai
import PyPDF2 as pp
from dotenv import load_dotenv
import os
load_dotenv()

text_to_num = {
    'curt': 150,
    'mitjà': 500,
    'llarg': 1000,
}

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
    with st.container(border=True):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            number = st.select_slider("Selecciona la llargada del resum", options=["curt", "mitjà", "llarg"], value="curt")
        with col2:
            lang = st.selectbox("Escull l'idioma", options=['Català', 'Español', 'English'], index=0)
    file = st.file_uploader("Introdueix aquí el fitxer '.pdf' per resumir.", type=[".pdf"])
    if file is not None:
        with st.spinner("Llegint..."):
            text = read_file(file)
        with st.spinner("Resumint..."):
            initial_message = {"role": "user", "content": f"""
            Resumeix el text següent de manera que quedin ben clares les idees principals en un màxim de {text_to_num[number]} paraules. 
            Escriu-ho tot en format markdown i utilitza les features de markdown, sobre tot bullet points i negretes. També els èmfasis de paraules ``.
            Fes-ho en l'idioma {lang}.
            
            {text}
            """}
            openai_client = openai.OpenAI(api_key=os.environ["OPENAI_APIKEY"])
            response = openai_client.chat.completions.create(model="gpt-4-1106-preview", messages=[initial_message])
            print(response.choices[0].message.content)
            st.markdown(response.choices[0].message.content)


if __name__ == '__main__':
    main()