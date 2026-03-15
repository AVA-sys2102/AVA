import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import io

load_dotenv()

class AvaEngine:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash" 

    def processar_multimodal(self, mensagem_usuario, contexto_texto="", imagem_bytes=None, audio_bytes=None, historico_anterior=[]):
        # Instrução de Sistema Avançada para melhor leitura
        instrucao_sistema = (
            "És a AVA (Advanced Virtual Assistant). A tua capacidade de leitura é superior.\n"
            "1. Analisa os documentos fornecidos com precisão cirúrgica.\n"
            "2. Se a informação estiver nos documentos, cita o nome do ficheiro.\n"
            "3. Se houver imagens, cruza os dados visuais com o texto.\n"
            "4. Mantém um tom profissional, mas amigável.\n"
        )

        conteudo_para_enviar = [instrucao_sistema]

        # Adicionar contexto documental estruturado
        if contexto_texto:
            conteudo_para_enviar.append(f"--- BIBLIOTECA DE CONTEXTO ---\n{contexto_texto}\n--- FIM DA BIBLIOTECA ---")

        # Adicionar Histórico (Memória de Longo Prazo) - limitamos às últimas 10 para focar na leitura atual
        for msg in historico_anterior[-10:]:
            conteudo_para_enviar.append(f"{msg['role'].upper()}: {msg['content']}")

        # Pergunta atual
        conteudo_para_enviar.append(f"UTILIZADOR: {mensagem_usuario}")

        # Ficheiros Multimodais (Visão e Voz)
        if imagem_bytes:
            conteudo_para_enviar.append(types.Part.from_bytes(data=imagem_bytes, mime_type="image/jpeg"))
        if audio_bytes:
            conteudo_para_enviar.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"))

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=conteudo_para_enviar,
                config=types.GenerateContentConfig(temperature=0.3) # Menos 'criatividade', mais 'precisão' na leitura
            )
            return response.text
        except Exception as e:
            if "429" in str(e): return "⚠️ Sistema sobrecarregado. Tenta em 1 minuto."
            return f"❌ Erro: {str(e)}"