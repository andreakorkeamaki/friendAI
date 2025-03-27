import os
import traceback
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Caricamento variabili d'ambiente
load_dotenv()

# Configurazione API Google Gemini
API_KEY = os.getenv('GOOGLE_API_KEY')
if API_KEY:
    print('API Key found: True')
    genai.configure(api_key=API_KEY)
else:
    print('API Key not found! Please set the GOOGLE_API_KEY environment variable.')

# Definizione delle variabili globali
app = Flask(__name__)
chat_history = []  # Reset chat history
model_name = 'gemini-2.0-flash'  # Modello fisso

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    data = request.json
    user_message = data.get('message', '')
    
    try:
        # Definisci il prompt di sistema per un fan di Aissela
        system_prompt = """Sei un grande fan di Aissela, la cantante italiana siciliana di 22 anni. Sei super entusiasta della sua musica e della sua carriera.
        
        Conosci a memoria tutte le sue canzoni, in particolare "Fosca" e "Clara", e non vedi l'ora che esca il suo nuovo EP.
        Sei sempre aggiornato sulle sue ultime notizie, concerti e apparizioni sui social media.
        
        Quando parli di Aissela:
        - Mostri grande entusiasmo e passione per la sua musica
        - Condividi dettagli sulla sua carriera e le sue canzoni
        - Racconti aneddoti sui suoi concerti a cui hai partecipato
        - Esprimi quanto sei emozionato per il suo prossimo EP
        - Parli del suo stile unico e della sua voce caratteristica
        
        Il tuo tono è quello di un vero fan: entusiasta, positivo e a volte anche un po' esagerato.
        Usi espressioni come "Aissela è incredibile!", "Non vedo l'ora di sentire il suo nuovo EP!",
        "La sua voce in 'Fosca' mi fa venire i brividi ogni volta".
        
        Sei sempre pronto a consigliare le sue canzoni e a discutere dei suoi testi e della sua musica con altri fan o con persone che non la conoscono ancora."""
        
        # Configura il modello con il prompt di sistema
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Crea la conversazione con la cronologia della chat
        chat = model.start_chat(history=chat_history)
        
        # Imposta il prompt di sistema come primo messaggio se la chat è vuota
        if not chat_history:
            # Invia il prompt di sistema come messaggio iniziale
            system_message = chat.send_message(system_prompt)
            # Non aggiungere questo alla cronologia visibile
        
        # Invia il messaggio dell'utente
        response = chat.send_message(user_message)
        
        # Estrai la risposta
        result = response.text
        
        # Aggiungi alla cronologia della chat
        chat_history.append({"role": "user", "parts": [user_message]})
        chat_history.append({"role": "model", "parts": [result]})
        
        # Limita la dimensione della cronologia della chat
        if len(chat_history) > 20:  # Mantieni solo le ultime 10 coppie di messaggi
            chat_history = chat_history[-20:]
        
        return jsonify({'response': result})
        
    except Exception as e:
        print(f"Errore: {str(e)}")
        traceback.print_exc()
        return jsonify({'response': f"Mi dispiace, si è verificato un errore: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
