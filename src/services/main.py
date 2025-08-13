def main():
    video_path = "../../video.mp4"
    
    print("🎬 Professional Video Analyzer")
    print("1. Extract regular frames")
    print("2. Smart scene detection")
    print("3. Play video with IA")
    print("4. Youtube player (Need URL)")
    
    choice = input("Choose option (1-4): ")
    
    if choice == "1":
        import frame_extractor
        frame_extractor.extract_key_frames(video_path, 5)
    elif choice == "2":
        import scene_detector
        scene_detector.extract_smart_frames(video_path, 5)
    elif choice == "3":
        import video_player
        video_player.player_com_ia(video_path, pasta_salvar="ai_frames")
    elif choice == "4":
        print("\n🎬 ANALISADOR DE VÍDEOS DO YOUTUBE")
        print("="*50)
        
        # Submenu para YouTube
        print("\n📺 Opções do YouTube:")
        print("a. 🎯 Análise completa (baixar + IA)")
        print("b. 📋 Apenas informações básicas")
        print("c. 🔙 Voltar ao menu principal")
        
        youtube_choice = input("\nEscolha uma opção (a/b/c): ").lower().strip()
        
        if youtube_choice == "c":
            print("🔙 Voltando ao menu principal...")
            main()  # Recursivo para voltar ao menu
        elif youtube_choice in ["a", "b"]:
            url = input("\n🔗 Digite a URL do vídeo YouTube: ").strip()
            if url:
                try:
                    import youtube_IA
                    analyzer = youtube_IA.YouTubeVideoAnalyzer()
                    
                    if youtube_choice == "a":
                        print("\n🎯 Iniciando análise completa...")
                        num_frames = input("📊 Quantos frames analisar? (padrão: 8): ").strip()
                        num_frames = int(num_frames) if num_frames.isdigit() else 8
                        
                        resumo = analyzer.analisar_url_youtube(url, baixar_video=True, num_frames=num_frames)
                    else:  # opção "b"
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
                        
                except ImportError:
                    print("❌ Erro: youtube_IA.py não encontrado!")
                    print("🔧 Certifique-se de que o arquivo youtube_IA.py está na pasta services/")
                except Exception as e:
                    print(f"❌ Erro inesperado: {str(e)}")
            else:
                print("❌ URL não pode estar vazia!")
        else:
            print("❌ Opção inválida!")

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()