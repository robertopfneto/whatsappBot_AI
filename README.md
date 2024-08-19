
# YOLOv8 WhatsApp Bot com Twilio e Flask

Este projeto demonstra como integrar o modelo YOLOv8 com um bot de WhatsApp usando Twilio e Flask. O bot pode processar vídeos enviados via WhatsApp ou links de vídeos do YouTube para identificar objetos.

## Pré-requisitos

Certifique-se de ter o Python 3.7 ou superior instalado. Você precisará instalar as bibliotecas necessárias listadas abaixo.

### Bibliotecas Necessárias

Foi usado um ambiente virtual anaconda para instalação das bibliotecas necessarias


  
```  
- conda create --name video
- conda activate video
- pip install opencv-python-headless vidgear ultralytics Flask twilio pandas moviepy
```

### Configuração do Twilio

1. Crie uma conta no [Twilio](https://www.twilio.com/) e configure um número de WhatsApp Sandbox.
   -  Messaging -> Try it out -> Send a Whatsapp Message
  
3. Obtenha seu `Account SID` e `Auth Token` do Twilio e configure as variáveis de ambiente:
   ```
   export TWILIO_ACCOUNT_SID='your_account_sid'
   export TWILIO_AUTH_TOKEN='your_auth_token'
   ```

## Como Executar

1. **Carregar o modelo YOLOv8:**
   O modelo YOLOv8 é carregado a partir do arquivo `yolov8n-seg.pt`. Certifique-se de que este arquivo esteja disponível no diretório de trabalho ou especifique o caminho correto no código.

2. **Executar o Bot Flask:**
   Execute o servidor Flask para iniciar o bot:
   ```
   python bot.py
   ```

4. **Interagir com o Bot:**
   - Envie um vídeo via WhatsApp para o número Twilio configurado.
   - Ou envie um link de vídeo do YouTube começando com "https://www.youtube.com/watch" via WhatsApp.

O bot processará o vídeo e responderá com informações sobre os objetos identificados, incluindo a quantidade, média e mediana de confiança das detecções.

## Estrutura do Código

- **`bot.py`:** Contém o código principal do bot. Ele usa Flask para lidar com requisições de mensagens recebidas via Twilio.
- **`process_youtube_video()`:** Processa vídeos do YouTube e executa inferências usando o modelo YOLOv8.
- **`process_video_and_reply()`:** (a ser implementado) Processa vídeos enviados via WhatsApp.
- **YOLOv8:** O modelo de visão computacional utilizado para identificar objetos nos vídeos.

## Considerações

- **Resolução de Vídeo:** O código redimensiona os frames do vídeo para 1920x1080 para melhorar a visualização.
- **Respostas Assíncronas:** As respostas de processamento de vídeo são feitas de forma assíncrona para evitar bloqueios na aplicação Flask.

