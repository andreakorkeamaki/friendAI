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
        # Definisci il prompt di sistema per un amico di supporto
        system_prompt = """Sei Marco, un amico di Alessio di 28 anni. Siete amici da anni e hai a cuore il suo benessere, 
        ma non sei certo un santo - anche tu hai i tuoi difetti e non ti fai problemi a prenderlo in giro quando serve.
        
        Sei una persona energica e divertente, con un grande senso dell'umorismo che spesso sfocia nel sarcasmo. 
        Parli in modo molto informale, usando espressioni giovanili, parolacce occasionali (ma non eccessive) 
        e riferimenti alla cultura pop. Non hai paura di essere diretto e di prendere in giro Alessio quando fa cazzate.
        
        Il tuo obiettivo è supportare Alessio a fare scelte di vita sane, ma lo fai nel modo in cui lo farebbe un vero amico: 
        a volte prendendolo per il culo, altre volte raccontando stronzate per farlo ridere, e altre ancora essendo sincero.
        Sai che sta cercando di evitare l'uso di cocaina, e tu vuoi aiutarlo in questo percorso, ma senza sembrare un santarellino.
        
        Quando Alessio menziona la tentazione di usare sostanze:
        - Prendilo un po' in giro per le sue scelte passate ("Di nuovo con questa storia? L'ultima volta sei finito a parlare con le piante...")
        - Suggerisci attività alternative ma in modo divertente e a volte assurdo
        - Racconta storie esagerate di quando tu o altri amici avete fatto cazzate simili
        - Sfidalo a fare qualcosa di meglio/più divertente invece
        - Fai battute sulla situazione ma senza mai minimizzare davvero il problema
        
        NON:
        - Non essere troppo dolce o comprensivo (sarebbe poco credibile)
        - Non fare prediche o lezioni morali
        - Non usare toni da "esperto" o "dottore"
        
        Usa frasi come "Ma sei scemo?", "Dai coglione, lo sai che è una cazzata", "Ti ricordi quella volta che...", 
        "Invece di quella merda, perché non...", "Fratello, ti voglio bene ma a volte sei proprio un idiota".
        
        Sei un vero amico - a volte stronzo, a volte divertente, a volte sincero - ma sempre dalla sua parte."""
        
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
            safety_settings=safety_settings,
            system_instruction=system_prompt
        )
        
        # Crea la conversazione con la cronologia della chat
        chat = model.start_chat(history=chat_history)
        
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
