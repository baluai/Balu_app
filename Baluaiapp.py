import os
import whisper
import pyodbc

# Configuración de la conexión a la base de datos
conn_str = (
    "Driver={SQL Server};"
    "Server=sql5110.site4now.net;"
    "Database=db_a76939_bbddproyecto;"
    "UID=db_a76939_bbddproyecto_admin;"
    "PWD=9!vXkv2212222;"
    "Trusted_Connection=no;"
)

# Cargar el modelo de transcripción de whisper
model = whisper.load_model("small")

# Consulta SQL para insertar nuevos registros en la tabla RegistroLlamadas
insert_query = "INSERT INTO RegistroLlamadas (Fecha, Transcripcion,NombreVendedor,NombreEmpresa, Proceso,NombreArchivo,IdEmpresa,IdVendedor) values (GETDATE(),?,?,?,?,?,3,18)"

# Ruta de la carpeta de archivos de audio
audio_folder = "C:\\Users\\cleme\\Desktop\\Audios Balu\\ICGroup\\100 grabaciones MCE para análisis_septiembre 2023\\"


try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # Recorrer todas las subcarpetas de audio_folder
    for root, _, _ in os.walk(audio_folder):

    # Obtén la lista de archivos de audio en la carpeta actual
        audio_files = [f for f in os.listdir(root) if f.lower().endswith(('.mp3', '.gsm', '.wav'))]
    
        for audio_file_name in audio_files:
            audio_file_path = os.path.join(root, audio_file_name)

            # Realiza la transcripción
            result = model.transcribe(audio_file_path, language="es")
            transcription_text = result["text"]

            #print(audio_file_path.encode('utf-8', 'ignore').decode('utf-8'))

            # Dividir la ruta del archivo en variables
       
            split_path = audio_file_path.split(os.path.sep)
            NombreArchivo = split_path[-1]  # Nombre de la empresa
            SubCarpeta1 = split_path[-2]  # Nombre del proceso
            SubCarpeta2 = split_path[-3]  # Nombre del vendedor
            SubCarpeta3 = split_path[-4]   # Nombre de la carpeta 1

         #C:\Users\cleme\Desktop\Audios Balu\ICGroup\100 grabaciones MCE para análisis_septiembre 2023\No Ventas

            # Dividir la fecha del nombre del archivo (suponiendo que la fecha está en el nombre)
            filename_parts = os.path.splitext(audio_file_name)[0].split('_')
            if len(filename_parts) >= 2:
               NVendedor = filename_parts[-1]
            else:
                NVendedor = 'No hay Nvendedor en el nombre'

             


            # Actualizar la base de datos con la respuesta generada
            cursor.execute(insert_query, transcription_text, NVendedor, SubCarpeta3,SubCarpeta2,NombreArchivo) 
            conn.commit()
            
except pyodbc.Error as ex:
    conn.rollback()  # En caso de error, se revierte la transacción
    print("Error de conexion o consulta:", ex)
