# Crear listas con caracteres reservados y palabras especiales del lenguaje
caracteres_reservados = ["(",")",":","-"]
comandos = ["defvar", "=", "move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
constantes = ["Dim", "myXpos", "myYpos", "myChips", "myBalloons", "balloonsHere", "ChipsHere", "Spaces"]
control = ["if", "loop", "repeat", "facing", "blocked", "can-put?", "can-pick?", "can-move?", "isZero", "not", "defun"]

#Tabla de simbolos para guardar las variables creadas por el usuario
tabla_simbolos = {}

#Agrego las contantes a mi tabla de simbolos para verificarlas al tiempo con las variables del usuario
for constante in constantes:
    tabla_simbolos[constante] = None
    
def parse(lexer_result):
    # Crear funcion para iniciar a analizar la sintaxis y usar las funciones de acuerdo al token identificado
    
    #Se comprueba que la cantidad de signos ( y ) sea consistente
    
    contar_parentesis(lexer_result)
    
    tokens = lexer_result.copy()
    instrucciones = []
    correctamente = []
    parentesis_abiertos = 0
    # Iterar sobre los tokens mientras que haya alguno sin procesar
    while len(tokens) > 0:
        # Revisar si inicia un paréntesis porque cada instrucción viene rodeada de uno
        token_actual = tokens.pop(0)
        if token_actual == "(":
            # Inicializar una lista para los tokens de un fragmento lógico
            fragmento_logico = []
            fragmento_logico.append(token_actual)
            parentesis_abiertos += 1
            
            # Repetir la extracción de paréntesis de inicio hasta llegar a una palabra reservada
            while tokens[0] == "(":
                fragmento_logico.append(tokens.pop(0))
                parentesis_abiertos += 1
                
            # Obtener el cuerpo principal de la instrucción, el primero que no es (
            principal = tokens.pop(0)
            fragmento_logico.append(principal)
            
            # Recorrer la instrucción mientras que no se cierre del todo
            while parentesis_abiertos > 0:
                token = tokens.pop(0)
                # Ajustar el contador según los paréntesis que encuentre
                if token == "(":
                    parentesis_abiertos += 1
                if token == ")":
                    parentesis_abiertos -= 1
                fragmento_logico.append(token)
            
            # En este punto, ya se habrá cerrado todo. Si no, seguiría en el ciclo
            instrucciones.append(fragmento_logico)
            
            # Verificar si el cuerpo principal es un comando, una función o un bloque de control
            # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
            if principal in comandos:
                correctamente.append(parse_comando(fragmento_logico))
            elif principal in control:
                correctamente.append(parse_control(fragmento_logico))
            else:
                correctamente.append(parse_funciones(fragmento_logico))

    # Estará bien escrito si no hay Falsos en la lista
    bien_escrito = False not in correctamente
    return bien_escrito
    
def parse_comando(instruccion):
    # verificar los comando pasa moverse derecha, izquierda, etc

    #verificar el uso de null
    if instruccion[1] == "null" and len(instruccion)==3:
        return True
    
    # Verificar si es una instrucción "defvar"
    elif instruccion[1] == "defvar":
        # Verificar si la instrucción tiene el formato correcto
        if len(instruccion) == 5 and instruccion[2].isidentifier() and instruccion[3].isdigit() and instruccion[2] not in tabla_simbolos.keys() and instruccion[2] not in constantes:
            nombre_variable = instruccion[2]
            valor_inicial = int(instruccion[3])
            #agregar el nuevo valor a la tabla de simbolos
            tabla_simbolos[nombre_variable]=valor_inicial  
            return True
    
    #verificar el uso correcto de la reasignacion de valores
    elif instruccion[1] == "=":
        if len(instruccion) == 5  and instruccion[3].isdigit() and instruccion[2] in tabla_simbolos.keys():
            tabla_simbolos[instruccion[2]]=int(instruccion[3])
            return True
    
    #verificar el uso correcto de las direcciones
    elif instruccion[1] in ["move", "skip", "turn", "face"]:
            if len(instruccion) == 4 and (instruccion[2].isdigit() or instruccion[2] in tabla_simbolos.keys()):
                return True
    #verificar el uso correcto del put y el pick
    elif instruccion[1] in ["put", "pick"]:
        if len(instruccion) == 4 and instruccion[2] in [":balloons", ":chips"]:
           if instruccion[3].isdigit() or instruccion[3]in tabla_simbolos.keys():
                    return True
        
    #verificar el uso correcto del move, run, move
    elif instruccion[1] in ["move-dir", "run-dirs", "move-face"] and len(instruccion) != 4:

        if instruccion[1] == "move-dir":
            if instruccion[2].isdigit() and instruccion[3] in [":front", ":right", ":left", ":back"]:

                return True
        elif instruccion[1] == "run-dirs":
            if len(instruccion) >= 4 and instruccion[-1] == ')':
                # Extraemos solo las direcciones de la lista de instrucción, excluyendo los paréntesis
                direcciones = instruccion[2:-1]
                # Verificamos que todas las direcciones sean válidas
                if all(dir in [":front", ":right", ":left", ":back",":up", ":down"] for dir in direcciones):
                    return True
        
        elif instruccion[1] == "move-face":
            if instruccion[2].isdigit() and instruccion[3] in [":north", ":south", ":west", ":east"]:

                return True
    
    #En caso de que no cumpla ninguno de estos casos se lanza la excepcion
    raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada")
    return None

def parse_control(instruccion):
    # verificar los comandos de control
    return None

def parse_funciones(instruccion):
    # verificar las funciones
    return None



def contar_parentesis(tokens):
    parentesisIniciales = sum(1 for token in tokens if token == '(')
    parentesisFinales = sum(1 for token in tokens if token == ')')
    if parentesisIniciales != parentesisFinales:
        raise Exception("La cantidad de paréntesis abiertos y cerrados no coincide.")

