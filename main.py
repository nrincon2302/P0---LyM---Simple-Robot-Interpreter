from logic import parse
import re

def app():


    print("\n*********************************************")
    print("*                                           *")
    print("*          Bienvenido al Analizador         *")
    print("*               Sintáctico                  *")
    print("*                                           *")
    print("*          Hecho por Carol Florido          *")
    print("*              y Nicolás Rincón Sánchez     *")
    print("*                                           *")
    print("*********************************************\n")
    
    #nombre_archivo=input("Ingrese el nombre del archivo: ")
    contenido = abrir_archivo("prueba.txt")
    tokens = tokenizador(contenido)
    for i in parse(tokens):
        print(i)

#Funcion para abrir un archivo en formato txt
def abrir_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
        return contenido
    except Exception as e:
        print(f"Ocurrió un error al intentar abrir el archivo: {e}")
        return None
    
#funcion para tokenizar el lenguaje del archivo
def tokenizador(contenido):
    # Convertir todo el contenido a minúsculas
    contenido = contenido.lower()
    
    # Tokenizar, incluyendo palabras específicas y paréntesis como tokens individuales
    tokens = re.findall(r'(can-put\?|can-pick\?|can-move\?|move-dir|move-face|run-dirs|:\w+|\b\w+\b|[()])', contenido)
    return tokens

app()
