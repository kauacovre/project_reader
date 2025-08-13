import os
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import json
import re

# Para download do YouTube
try:
    import yt_dlp
    YTDLP_DISPONIVEL = True
    print("✅ yt-dlp disponível!")
except ImportError:
    YTDLP_DISPONIVEL = False
    print("❌ Para baixar do YouTube, instale: pip install yt-dlp")

# Para IA local
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from PIL import Image
    BLIP_DISPONIVEL = True
    print("✅ BLIP disponível!")
except ImportError:
    BLIP_DISPONIVEL = False
    print("❌ Para IA, instale: pip install transformers torch pillow")

class YouTubeVideoAnalyzer:
    def __init__(self, pasta_downloads: str = "youtube_downloads"):
        """
        Analisador de vídeos do YouTube com IA
        Args:
            pasta_downloads: Pasta onde salvar os vídeos baixados
        """
        self.pasta_downloads = pasta_downloads
        self.pasta_frames = os.path.join(pasta_downloads, "frames")
        self.pasta_resumos = os.path.join(pasta_downloads, "resumos")
        
        # Criar pastas necessárias
        for pasta in [self.pasta_downloads, self.pasta_frames, self.pasta_resumos]:
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                print(f"📁 Pasta criada: {pasta}")
        
        # Inicializar IA se disponível
        if BLIP_DISPONIVEL:
            print("🤖 Carregando modelo BLIP...")
            try:
                self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                print("✅ Modelo BLIP carregado!")
                self.ia_disponivel = True
            except Exception as e:
                print(f"❌ Erro ao carregar BLIP: {e}")
                self.ia_disponivel = False
        else:
            self.ia_disponivel = False
    
    def obter_info_video(self, url: str) -> Dict:
        """Obtém informações do vídeo do YouTube"""
        if not YTDLP_DISPONIVEL:
            return {"erro": "yt-dlp não instalado"}
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                dados = {
                    'titulo': info.get('title', 'Título não encontrado'),
                    'canal': info.get('uploader', 'Canal não encontrado'),
                    'duracao': info.get('duration', 0),
                    'visualizacoes': info.get('view_count', 0),
                    'descricao': info.get('description', '')[:500] + '...' if info.get('description') else 'Sem descrição',
                    'data_upload': info.get('upload_date', 'Data não encontrada'),
                    'id_video': info.get('id', 'ID não encontrado'),
                    'url_thumbnail': info.get('thumbnail', '')
                }
                
                return dados
        except Exception as e:
            return {"erro": f"Erro ao obter informações: {str(e)}"}
    
    def baixar_video(self, url: str, qualidade: str = "worst[height<=480]") -> str:
        """
        Baixa vídeo do YouTube
        Args:
            url: URL do vídeo
            qualidade: Qualidade do vídeo (worst[height<=480] para economia)
        Returns:
            Caminho do arquivo baixado
        """
        if not YTDLP_DISPONIVEL:
            print("❌ yt-dlp não instalado!")
            return None
        
        # Gerar nome de arquivo seguro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"video_{timestamp}.%(ext)s"
        caminho_arquivo = os.path.join(self.pasta_downloads, nome_arquivo)
        
        ydl_opts = {
            'format': qualidade,  # Baixa em qualidade menor para economia
            'outtmpl': caminho_arquivo,
            'quiet': False,
        }
        
        try:
            print("📥 Baixando vídeo do YouTube...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Encontrar o arquivo baixado
            base_nome = nome_arquivo.replace('.%(ext)s', '')
            for arquivo in os.listdir(self.pasta_downloads):
                if arquivo.startswith(f"video_{timestamp}"):
                    caminho_final = os.path.join(self.pasta_downloads, arquivo)
                    print(f"✅ Vídeo baixado: {arquivo}")
                    return caminho_final
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao baixar vídeo: {str(e)}")
            return None
    
    def extrair_frames_chave(self, caminho_video: str, num_frames: int = 10) -> List[np.ndarray]:
        """Extrai frames importantes do vídeo"""
        video = cv2.VideoCapture(caminho_video)
        if not video.isOpened():
            return []
        
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            return []
        
        # Distribuir frames ao longo do vídeo
        indices_frames = np.linspace(0, total_frames-1, num_frames, dtype=int)
        
        frames = []
        for idx in indices_frames:
            video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = video.read()
            if ret:
                frames.append(frame)
        
        video.release()
        return frames
    
    def analisar_frame_ia(self, frame: np.ndarray) -> str:
        """Analisa um frame com IA"""
        if not self.ia_disponivel:
            return "IA não disponível"
        
        try:
            # Converter BGR para RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagem_pil = Image.fromarray(frame_rgb)
            
            # Gerar descrição
            inputs = self.processor(imagem_pil, return_tensors="pt")
            output = self.model.generate(**inputs, max_length=50, num_beams=5)
            descricao = self.processor.decode(output[0], skip_special_tokens=True)
            
            return descricao
        except Exception as e:
            return f"Erro na análise: {str(e)}"
    
    def gerar_resumo_video(self, caminho_video: str, info_video: Dict, num_frames: int = 8) -> Dict:
        """Gera resumo completo do vídeo"""
        print(f"🎬 Analisando vídeo: {info_video.get('titulo', 'Vídeo sem título')}")
        print(f"📊 Extraindo {num_frames} frames para análise...")
        
        frames = self.extrair_frames_chave(caminho_video, num_frames)
        if not frames:
            return {"erro": "Não foi possível extrair frames"}
        
        print(f"🤖 Analisando {len(frames)} frames com IA...")
        
        # Analisar frames com IA
        descricoes_frames = []
        if self.ia_disponivel:
            for i, frame in enumerate(frames):
                print(f"   Analisando frame {i+1}/{len(frames)}...")
                descricao = self.analisar_frame_ia(frame)
                descricoes_frames.append({
                    'frame': i+1,
                    'tempo_aproximado': f"{(i * info_video.get('duracao', 0) / len(frames) / 60):.1f}min",
                    'descricao': descricao
                })
        else:
            descricoes_frames = [{"erro": "IA não disponível para análise de frames"}]
        
        # Salvar alguns frames como exemplo
        frames_salvos = []
        for i, frame in enumerate(frames[:5]):  # Salvar apenas 5 frames
            nome_frame = f"frame_{i+1:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            caminho_frame = os.path.join(self.pasta_frames, nome_frame)
            if cv2.imwrite(caminho_frame, frame):
                frames_salvos.append(nome_frame)
        
        # Análise de palavras-chave
        palavras_frequentes = {}
        if self.ia_disponivel:
            for desc in descricoes_frames:
                palavras = desc['descricao'].lower().split()
                for palavra in palavras:
                    if len(palavra) > 3 and palavra.isalpha():
                        palavras_frequentes[palavra] = palavras_frequentes.get(palavra, 0) + 1
        
        palavras_top = sorted(palavras_frequentes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Montar resumo final
        resumo = {
            'info_video': info_video,
            'analise': {
                'data_analise': datetime.now().isoformat(),
                'total_frames_analisados': len(frames),
                'frames_salvos': frames_salvos,
                'ia_disponivel': self.ia_disponivel
            },
            'descricoes_frames': descricoes_frames,
            'palavras_chave': [palavra for palavra, freq in palavras_top],
            'resumo_geral': self._gerar_resumo_textual(info_video, descricoes_frames, palavras_top)
        }
        
        return resumo
    
    def _gerar_resumo_textual(self, info_video: Dict, descricoes: List, palavras_top: List) -> str:
        """Gera resumo em texto legível"""
        titulo = info_video.get('titulo', 'Vídeo sem título')
        canal = info_video.get('canal', 'Canal desconhecido')
        duracao_min = info_video.get('duracao', 0) // 60
        
        resumo = f"📹 RESUMO DO VÍDEO YOUTUBE\n"
        resumo += f"{'='*60}\n\n"
        resumo += f"🎬 Título: {titulo}\n"
        resumo += f"📺 Canal: {canal}\n"
        resumo += f"⏱️ Duração: {duracao_min} minutos\n"
        resumo += f"👁️ Visualizações: {info_video.get('visualizacoes', 'N/A'):,}\n"
        resumo += f"📅 Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        if self.ia_disponivel and len(descricoes) > 0 and 'erro' not in descricoes[0]:
            resumo += f"🤖 ANÁLISE VISUAL POR IA:\n"
            resumo += f"{'-'*40}\n"
            for desc in descricoes[:5]:  # Mostrar apenas 5 primeiras
                resumo += f"⏰ {desc['tempo_aproximado']}: {desc['descricao']}\n"
            
            if palavras_top:
                resumo += f"\n🎯 PALAVRAS-CHAVE IDENTIFICADAS:\n"
                resumo += f"{'-'*40}\n"
                palavras_str = ', '.join([palavra for palavra, _ in palavras_top[:8]])
                resumo += f"{palavras_str}\n"
            
            resumo += f"\n📝 RESUMO GERAL:\n"
            resumo += f"{'-'*40}\n"
            resumo += f"Este vídeo do YouTube de {duracao_min} minutos do canal '{canal}' "
            resumo += f"contém principalmente elementos relacionados a: {', '.join([p[0] for p in palavras_top[:3]])}. "
            resumo += f"A análise visual identificou {len(descricoes)} cenas distintas ao longo do vídeo."
        else:
            resumo += f"⚠️ Análise visual não disponível (IA não carregada)\n"
            resumo += f"📝 Informações básicas extraídas dos metadados do YouTube."
        
        return resumo
    
    def salvar_resumo(self, resumo: Dict, nome_arquivo: str = None) -> str:
        """Salva o resumo em arquivo"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"resumo_youtube_{timestamp}"
        
        # Salvar JSON completo
        caminho_json = os.path.join(self.pasta_resumos, f"{nome_arquivo}.json")
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(resumo, f, ensure_ascii=False, indent=2)
        
        # Salvar resumo em texto legível
        caminho_txt = os.path.join(self.pasta_resumos, f"{nome_arquivo}.txt")
        with open(caminho_txt, 'w', encoding='utf-8') as f:
            f.write(resumo['resumo_geral'])
        
        print(f"💾 Resumo salvo em:")
        print(f"   📄 Texto: {caminho_txt}")
        print(f"   📊 Dados: {caminho_json}")
        
        return caminho_txt
    
    def analisar_url_youtube(self, url: str, baixar_video: bool = True, num_frames: int = 8) -> Dict:
        """
        Função principal - analisa vídeo do YouTube completo
        Args:
            url: URL do vídeo do YouTube
            baixar_video: Se deve baixar o vídeo (True) ou usar apenas metadados (False)
            num_frames: Número de frames para análise visual
        Returns:
            Dicionário com resumo completo
        """
        print("🚀 Iniciando análise do vídeo YouTube...")
        print(f"🔗 URL: {url}")
        
        # 1. Obter informações básicas
        print("\n📋 Obtendo informações do vídeo...")
        info_video = self.obter_info_video(url)
        if 'erro' in info_video:
            return info_video
        
        print(f"✅ Título: {info_video['titulo']}")
        print(f"✅ Canal: {info_video['canal']}")
        print(f"✅ Duração: {info_video['duracao']//60}min {info_video['duracao']%60}s")
        
        if not baixar_video:
            # Retornar apenas informações básicas
            return {
                'info_video': info_video,
                'resumo_geral': self._gerar_resumo_textual(info_video, [], []),
                'analise_visual': False
            }
        
        # 2. Baixar vídeo
        print("\n📥 Baixando vídeo...")
        caminho_video = self.baixar_video(url)
        if not caminho_video:
            return {"erro": "Falha ao baixar vídeo"}
        
        # 3. Analisar com IA
        print("\n🤖 Iniciando análise visual com IA...")
        resumo = self.gerar_resumo_video(caminho_video, info_video, num_frames)
        
        # 4. Salvar resumo
        print("\n💾 Salvando resumo...")
        nome_arquivo = re.sub(r'[<>:"/\\|?*]', '_', info_video['titulo'])[:50]
        self.salvar_resumo(resumo, nome_arquivo)
        
        # 5. Limpeza opcional (remover vídeo baixado)
        print(f"\n🗑️ Arquivo de vídeo mantido em: {caminho_video}")
        print("   (você pode deletar manualmente se quiser economizar espaço)")
        
        return resumo

def main():
    """Interface principal"""
    print("🎬 ANALISADOR DE VÍDEOS DO YOUTUBE COM IA")
    print("="*50)
    
    # Verificar dependências
    if not YTDLP_DISPONIVEL:
        print("❌ ERRO: yt-dlp não está instalado!")
        print("🔧 Instale com: pip install yt-dlp")
        return
    
    # Inicializar analisador
    analyzer = YouTubeVideoAnalyzer()
    
    while True:
        print("\n📺 OPÇÕES:")
        print("1. 🎯 Análise completa (baixar + IA)")
        print("2. 📋 Apenas informações básicas")
        print("3. 🚪 Sair")
        
        escolha = input("\nEscolha uma opção (1-3): ").strip()
        
        if escolha == "3":
            print("👋 Até logo!")
            break
        
        if escolha not in ["1", "2"]:
            print("❌ Opção inválida!")
            continue
        
        url = input("\n🔗 Digite a URL do vídeo YouTube: ").strip()
        if not url:
            print("❌ URL não pode estar vazia!")
            continue
        
        try:
            if escolha == "1":
                print("\n🎯 Iniciando análise completa...")
                num_frames = input("📊 Quantos frames analisar? (padrão: 8): ").strip()
                num_frames = int(num_frames) if num_frames.isdigit() else 8
                
                resumo = analyzer.analisar_url_youtube(url, baixar_video=True, num_frames=num_frames)
            else:
                print("\n📋 Obtendo apenas informações básicas...")
                resumo = analyzer.analisar_url_youtube(url, baixar_video=False)
            
            if 'erro' in resumo:
                print(f"❌ Erro: {resumo['erro']}")
            else:
                print("\n" + "="*60)
                print("🎯 RESUMO GERADO:")
                print("="*60)
                print(resumo['resumo_geral'])
                print("="*60)
        
        except KeyboardInterrupt:
            print("\n⏹️ Operação cancelada pelo usuário.")
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")