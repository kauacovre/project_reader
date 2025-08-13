import cv2
import os
import numpy as np
from datetime import datetime
from typing import List

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from PIL import Image
    BLIP_DISPONIVEL = True
    print("✅ BLIP carregado com sucesso!")
except ImportError:
    BLIP_DISPONIVEL = False
    print("❌ Para usar IA, instale: pip install transformers torch pillow")

class VideoAI:
    def __init__(self):
        """Inicializa a IA BLIP"""
        
        if BLIP_DISPONIVEL:
            print("Carregando modelo BLIP (pode demorar na primeira vez)... ")
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            print("✅ Modelo BLIP carregado!")
        else:
            self.processor = None
            self.model = None

    def extrair_frames_chave(self, caminho_video: str, num_frames: int = 8) -> List[np.ndarray]:
        """Extrai frames importantes do vídeo"""

        video = cv2.VideoCapture(caminho_video)
        if not video.isOpened():
            return []
        
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        indices_frames = np.linspace(0, total_frames-1, num_frames, dtype=int)
        
        frames = []
        for idx in indices_frames:
            video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = video.read()

            if ret:
                frames.append(frame)
            
        video.release()
        return frames

    def analisar_frame(self, frame: np.ndarray) -> str:
        """Analisa um frame individual"""

        if not BLIP_DISPONIVEL or self.model is None:
            return "Modelo não disponível"
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem_pil = Image.fromarray(frame_rgb)

        inputs = self.processor(imagem_pil, return_tensors="pt")
        output = self.model.generate(**inputs, max_length=50, num_beams=5)
        descricao = self.processor.decode(output[0], skip_special_tokens=True)

        return descricao
    
    def resumir_video(self, caminho_video: str, num_frames: int = 8) -> str:
        """Analisa e resume o video completo"""

        print(f"🎬 Analisando vídeo: {os.path.basename(caminho_video)}")
        print(f"📊 Extraindo {num_frames} frames principais...")

        frames = self.extrair_frames_chave(caminho_video, num_frames)

        if not frames:
            return "❌ Erro: Não conseguiu extrair frames do vídeo"
        
        print(f"🤖 Analisando {len(frames)} frames com IA...")

        descricoes = []
        for i, frame in enumerate(frames):
            print(f"   Analisando frame {i+1}/{len(frames)}...")
            descricao = self.analisar_frame(frame)
            descricoes.append(f"🎞️ Frame {i+1}: {descricao}")

        resumo = f"📹 RESUMO DO VÍDEO\n"
        resumo += f"{'='*50}\n"
        resumo += f"Arquivo: {os.path.basename(caminho_video)}\n"
        resumo += f"Frames analisados: {len(frames)}\n"
        resumo += f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        resumo += "🔍 DESCRIÇÕES POR FRAME:\n"
        resumo += "-" * 30 + "\n"
        for desc in descricoes:
            resumo += desc + "\n"

        palavras_comuns = {}
        for desc in descricoes:
            palavras = desc.lower().split()
            for palavra in palavras:
                if len(palavra) > 3 and palavra.isalpha():
                    palavras_comuns[palavra] = palavras_comuns.get(palavra, 0) + 1
        
        if palavras_comuns:
            mais_comuns = sorted(palavras_comuns.items(), key=lambda x: x[1], reverse=True)[:5]
            resumo += f"\n🎯 RESUMO GERAL:\n"
            resumo += f"O vídeo parece conter principalmente: {', '.join([p[0] for p in mais_comuns])}\n"
        
        return resumo
    
def player_com_ia(caminho_video: str, pasta_salvar: str = "frames_salvos"):
    """Player de vídeo com análise de IA"""

    if not os.path.exists(pasta_salvar):
        os.makedirs(pasta_salvar)
        print(f"📁 Pasta criada: {pasta_salvar}")

    video = cv2.VideoCapture(caminho_video)
    if not video.isOpened():
        print("❌ Não conseguiu abrir o arquivo!")
        return False
    
    print("🎬 Controles do Player com IA:")
    print("- ESPAÇO: pausar/continuar")
    print("- 'q': sair")
    print("- 's': salvar frame atual")
    print("- 'i': analisar vídeo com IA 🤖")
    print(f"- Frames salvos em: {pasta_salvar}/")

    pausado = False
    contador_frame = 0
    frames_salvos = 0

    ia = VideoAI()
    
    while True:
        if not pausado:
            ret, frame = video.read()

            if not ret:
                print("🏁 Fim do vídeo!")
                break
            contador_frame += 1
        
        cv2.imshow("🤖 Player com IA", frame)

        tecla = cv2.waitKey(30) & 0xFF

        if tecla == ord('q'):
            break

        elif tecla == ord(' '):
            pausado = not pausado
            status = "⏸️ Pausado" if pausado else "▶️ Reproduzindo"
            print(f"Status: {status}")
        
        elif tecla == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"frame_{contador_frame:06d}_{timestamp}.jpg"
            caminho_arquivo = os.path.join(pasta_salvar, nome_arquivo)

            sucesso = cv2.imwrite(caminho_arquivo, frame)

            if sucesso:
                frames_salvos += 1
                print(f"✅ Frame salvo: {nome_arquivo}")
            
            else: 
                print(f"❌ Falha ao salvar: {nome_arquivo}")

        elif tecla == ord('i'):
            if BLIP_DISPONIVEL:
                print("🤖 Iniciando análise com IA...")
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)

                resumo = ia.resumir_video(caminho_video, num_frames=6)
                print("\n" + "="*60)
                print(resumo)
                print("="*60 + "\n")

                arquivo_resumo = os.path.join(pasta_salvar, f"resumo_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                with open(arquivo_resumo, 'w', encoding='utf-8') as f:
                    f.write(resumo)
                print(f"💾 Resumo salvo em: {arquivo_resumo}")
            
            else: 
                print("❌ IA não disponível. Instale: pip install transformers torch pillow")

    cv2.destroyAllWindows()
    video.release()
    print(f"🏁 Player fechado. Frames salvos: {frames_salvos}")
    return True