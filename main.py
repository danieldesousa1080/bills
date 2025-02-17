import cv2
from pyzbar import pyzbar
import numpy as np
from scrapper import *
from dotenv import dotenv_values


config = dotenv_values()

def ler_qrcode_camera():
    # Inicializa a câmera (0 é geralmente a câmera padrão)

    camera_str = config["CAMERA"] if config["CAMERA"] != "local" else 0

    camera = cv2.VideoCapture(camera_str)

    print("[INFO] Aponte a câmera para o QR Code. Pressione 'q' para sair.")

    while True:
        # Captura um frame da câmera
        ret, frame = camera.read()
        if not ret:
            print("[ERRO] Falha ao capturar imagem da câmera.")
            break

        # Decodifica os QR Codes no frame atual
        qr_codes = pyzbar.decode(frame)

        # Processa cada QR Code encontrado
        for qr_code in qr_codes:
            # Extrai os dados do QR Code
            dados = qr_code.data.decode('utf-8')
            tipo = qr_code.type
            
            # Imprime as informações no terminal
            get_bill_info(str(dados))
            exit()

            # Desenha um retângulo ao redor do QR Code na imagem
            pontos = qr_code.polygon
            if len(pontos) == 4:  # Certifica-se de que há 4 vértices
                pts = [(ponto.x, ponto.y) for ponto in pontos]
                pts = np.array(pts, dtype=np.int32)
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

            # Escreve o conteúdo do QR Code na imagem
            cv2.putText(frame, dados, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Exibe o frame com os QR Codes detectados
        cv2.imshow("Leitor de QR Code", frame)

        # Sai do loop se a tecla 'q' for pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera a câmera e fecha as janelas
    camera.release()
    cv2.destroyAllWindows()

# Chama a função para iniciar a leitura ao vivo
ler_qrcode_camera()
