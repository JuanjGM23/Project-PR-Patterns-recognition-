import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler
import joblib
from scipy.stats import skew
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from tkinter import PhotoImage
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from PIL import Image, ImageTk


"""
-------------------------------------------------------------------------------
* Título: Sistema de Control de Emergencias (Talanqueras)
* Autor: Juan Jose Gañan. Ingenieria de Software 
* Año: Mayo de 2024
* Descripción: Este software utiliza técnicas de procesamiento de audio y 
             aprendizaje automático para detectar sonidos de emergencia 
             (como ambulancias y camiones de bomberos) y simular la elevación 
             de talanqueras en la ciudad de Medellín.

* Modelo:
    - models/2modelo_entrenado_Audio.pkl: Modelo entrenado para la predicción de sonidos.
    - models/scaler_audio.pkl: Scaler utilizado para normalizar las características del audio.

* Licencia: MIT License
-------------------------------------------------------------------------------
"""

# # # https://librosa.org/doc/latest/feature.html

# Funcion para extraer caracterssticas de un archivo de audio
def extract_features(audio_file, muestreo=100000):
    señal, sr = librosa.load(audio_file, sr=None)
    señal_new = np.resize(señal, muestreo)

    # Extraccion  de caracteristicas
    varianza = np.var(señal_new)
    desviacion = np.std(señal_new)
    rms_amplitude = np.sqrt(np.mean(np.square(señal_new)))
    zero_crossings = np.where(np.diff(np.sign(señal_new)))[0]
    zcr = len(zero_crossings)
    skewness_value = skew(señal_new)
    # Nuevos descriptores
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=señal_new, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=señal_new, sr=sr))
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=señal_new, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=señal_new, sr=sr)) #  caida espectral
    mfccs = np.mean(librosa.feature.mfcc(y=señal_new, sr=sr), axis=1)[0]  # Solo el primer coeficiente MFCC - Coeficientes Cepstrales en la Escala de Mel

    return [varianza, desviacion, rms_amplitude, zcr, skewness_value, spectral_centroid, spectral_bandwidth,
            spectral_contrast, spectral_rolloff, mfccs]

# Cargamos modelo
modelo_entrenado = joblib.load('models/2modelo_entrenado_Audio.pkl')
scaler = joblib.load('models/scaler_audio.pkl')

# Realizamos simulacion de talanquera
def simular_talanquera(estado):
    if estado == 'abajo':
        #print("La talanquera está bajada.")
        label_resultado.config(text="La talanquera se ha bajado.")
    elif estado == 'arriba':
        #print("La talanquera se ha elevado.")
        label_resultado.config(text="La talanquera se ha elevado.")


# Funcion que nos sirve para predecir si es un sonido de emergencia
def predecir_sonido(caracteristicas):
    # Transformamos las nuevas caracteristicas utilizando el StandardScaler ajustado
    caracteristicas_normalized = scaler.transform(np.array([caracteristicas]))
    # Predecimos la clase del archivo de audio, bien sea 0,1,2
    prediccion = modelo_entrenado.predict(caracteristicas_normalized)
    return prediccion[0]

# Funcion que nos permite abrir un archivo y realizar la prediccion
def abrir_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.flac")]) # Validacion de archivos
    if archivo:
        caracteristicas = extract_features(archivo)
        prediccion = predecir_sonido(caracteristicas)
        etiqueta_predicha = clases[prediccion]
        print(f"Clase predicha: {prediccion}\nEtiqueta predicha: {etiqueta_predicha}")
        label_resultado_car.config(text=f"Carro de emergencia detectado: {etiqueta_predicha}")

        if prediccion in [0, 1]:  
            threading.Thread(target=simular_talanquera, args=('arriba',)).start()
            ventana.after(5000, lambda: simular_talanquera('abajo'))  # Baja la talanquera despues de 5 segundos
        else:
            messagebox.showinfo("Resultado", "No se detectó sonido de carro de emergencia.", icon="warning")



# Creamos la ventana principal
ventana = tk.Tk()
ventana.title("Detección de Sonido de Emergencia")

# Titulo
titulo = tk.Label(ventana, text="Sistema de Control de Emergencias", font=("Helvetica", 18))
titulo.place(x=30, y=20)  

titulo = tk.Label(ventana, text="(Talanqueras Ciudad Medellín)", font=("Helvetica", 10))
titulo.place(x=120, y=48)  

titulo = tk.Label(ventana, text="Tarea en ejecución: ", font=("Helvetica", 10))
titulo.place(x=25, y=115) 

# Botón para cargar el archivo de audio
btn_cargar_audio = tk.Button(ventana, text="Cargar Audio", command=abrir_archivo)
btn_cargar_audio.place(x=25, y=75)  

# Etiqueta para mostrar el resultado de la predicción
label_resultado = tk.Label(ventana, text="")
label_resultado.place(x=150, y=115)

label_resultado_car = tk.Label(ventana, text="")
label_resultado_car.place(x=150, y=135) 

titulo = tk.Label(ventana, text="Llamada de emergencia a: ", font=("Helvetica", 14))
titulo.place(x=110, y=200)  

titulo = tk.Label(ventana, text="The MIT License - v1", font=("Helvetica", 8))
titulo.place(x=0, y=282) 


# Para cargar una imagen de fondo
def cargar_imagen_fondo():
    imagen_fondo = tk.PhotoImage(file="img/tala.png").subsample(8,8) 
    label_fondo.configure(image=imagen_fondo)
    label_fondo.image = imagen_fondo 

# Etiqueta para la imagen de fondo
imagen_fondo = tk.PhotoImage(file="img/tala.png").subsample(8,8)  
label_fondo = tk.Label(ventana, image=imagen_fondo)
label_fondo.place(x=0, y=199)  


# Funcion para simular la llamada a la policia
def llamar_policia():
    label_resultado.config(text="Llamando a la Policía...")
btn_llamar_policia = tk.Button(ventana, text="Policía", command=llamar_policia)
btn_llamar_policia.place(x=115, y=250)


# llamada a la Fuerza Aerea
def llamar_fuerza_aerea():
    label_resultado.config(text="Llamando a la Fuerza Aérea...")
btn_llamar_fuerza_aerea = tk.Button(ventana, text="Fuerza Aérea", command=llamar_fuerza_aerea)
btn_llamar_fuerza_aerea.place(x=170, y=250)


# llamada a la Atención de Desastres
def llamar_atencion_desastres():
    label_resultado.config(text="Llamando a Atención de Desastres...")
btn_llamar_atencion_desastres = tk.Button(ventana, text="Atención de Desastres", command=llamar_atencion_desastres)
btn_llamar_atencion_desastres.place(x=255, y=250)


# llamada a la GAULA
def llamar_gaula():
    label_resultado.config(text="Llamando al GAULA...")
btn_llamar_gaula = tk.Button(ventana, text="GAULA", command=llamar_gaula)
btn_llamar_gaula.place(x=390, y=250)


# Funcion para hacer reset a la aplicación
def reset_aplicacion():
    # Nos sirve para limpiar los textos de los labels
    label_resultado.config(text="")
    label_resultado_car.config(text="")
icono_reset = tk.PhotoImage(file="img/reset.png")
btn_reset = tk.Button(ventana, image=icono_reset, command=reset_aplicacion)
btn_reset.place(x=400, y=50)

# Diccionario de las clases
clases = {0: 'Ambulancia', 1: 'Carro de bomberos', 2: 'Tráfico normal'}
ventana.geometry("450x300")

# Bloquear el cambio de tamaño de la ventana
ventana.resizable(width=False, height=False)
ventana.mainloop()
