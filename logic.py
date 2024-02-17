import copy

# ============================================================
# PALABRAS RESERVADAS
# ============================================================

# Crear listas con caracteres reservados y palabras especiales del lenguaje
caracteres_reservados = ["(",")",":","-"]
comandos = ["defvar", "=", "move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
comandosfunciones = ["move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
constantes = ["dim", "myxpos", "myypos", "mychips", "myballoons", "balloonshere", "chipshere", "spaces"]
control = ["if", "loop", "repeat"]
condition = ["facing?", "blocked?", "can-put?", "can-pick?", "can-move?", "iszero?", "not"]


# ============================================================
# ESTRUCTURAS AUXILIARES
# ============================================================

# Tabla de simbolos para guardar las variables creadas por el usuario
tabla_simbolos = {}

# Diccionario para guardar las funciones junto con la cantidad de parametros que tiene
funcionesNumParametros = {}

# Agrego las contantes a mi tabla de simbolos para verificarlas al tiempo con las variables del usuario
# Una constante no tiene un valor asignado, pero se puede utilizar en la sintaxis
for constante in constantes:
    tabla_simbolos[constante] = None
    
    
# ---------------------------------------------------------------------
# Inicio de las funciones del Parser
# ---------------------------------------------------------------------
def parse(lexer_result):
    # ============================================================
    # CASO 0a: El programa vacío es válido
    # ============================================================
    # Verificar que el lexer retorne algo. Si no, es vacío y es válido
    if len(lexer_result) == 0:
        return True
    
    # ============================================================
    # CASO 0b: Los signos ( y ) deben estar emparejados
    # ============================================================
    # Se llama a la función que verifica el emparejamiento de paréntesis
    # Si no, lanza una excepción que detiene la ejecución en este punto
    contar_parentesis(lexer_result)
    
    # ============================================================
    # EL PROGRAMA CUMPLE LAS CONDICIONES MÍNIMAS -> SE ANALIZA
    # ============================================================
    # Creación de variables auxiliares y una copia para tener lista mutable
    tokens = lexer_result.copy()
    instrucciones = []
    principales = []
    correctamente = []
    parentesis_abiertos = 0
    
    # Iterar sobre los tokens mientras que haya alguno sin procesar
    # Cada vez que itere, necesariamente estará en otra instrucción
    while len(tokens) > 0:
        # Revisar si inicia con un paréntesis porque cada instrucción viene rodeada de uno
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
                
            # Obtener el cuerpo principal de la instrucción, el primer token que no es (
            principal = tokens.pop(0)
            fragmento_logico.append(principal)
            principales.append(principal)
            
            # Recorrer la instrucción mientras que no se cierre del todo
            while parentesis_abiertos > 0:
                token = tokens.pop(0)
                # Ajustar el contador según los paréntesis que encuentre
                if token == "(":
                    parentesis_abiertos += 1
                if token == ")":
                    parentesis_abiertos -= 1
                # Independientemente, adjuntar el token al fragmento analizado
                fragmento_logico.append(token)
            
            # En este punto, ya se habrá cerrado todo. Si no, seguiría en el ciclo
            # Por ende, podemos agregar todo el fragmento lógico completo al conjunto de instrucciones
            instrucciones.append(fragmento_logico)
            
            # Verificar si el cuerpo principal es un comando, una función o un bloque de control
            # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
            
            # ============================================================
            # CASO 1: El fragmento lógico es un COMANDO
            # ============================================================
            if principal in comandos:
                correctamente.append(parse_comando(fragmento_logico, principal))
            # ============================================================
            # CASO 2: El fragmento lógico es un BLOQUE DE CONTROL
            # ============================================================
            elif principal in control:
                correctamente.append(parse_control(fragmento_logico, principal))
            # ============================================================
            # CASO 3: El fragmento lógico es una SIGNACIÓN DE FUNCIÓN
            # ============================================================
            elif principal == "defun":
                correctamente.append(parse_funciones(fragmento_logico))
            # ============================================================
            # CASO 4: El fragmento lógico es una FUNCIÓN DECLARADA
            # ============================================================
            elif principal in funcionesNumParametros:
                correctamente.append(parse_funciones(fragmento_logico))
            # ============================================================
            # CASO 5: El principal no corresponde a ninguna instrucción
            # ============================================================
            # Se lanza una excepción y se detiene la ejecución en este punto
            else:
                raise Exception(f"{fragmento_logico} no se reconoce este tipo de instrucción")  

    # Estará bien escrito si no hay Falsos en la lista
    bien_escrito = False not in correctamente
    return bien_escrito
    

# ---------------------------------------------------------------------
# Parser de comandos
# ---------------------------------------------------------------------
def parse_comando(instruccion, principal):
    # Identificar la posición en la que empieza el principal
    i = instruccion.index(principal)
    
    # ============================================================
    # CASO 1a: El comando tiene un principal nulo
    # ============================================================
    # Si es un nulo, lo define la gramática {S},{null,(,)},{S->(S); S->(null)}
    # Es decir, habrá siempre un número impar de símbolos terminales
    if principal == "null" and len(instruccion)%2 == 1:
        # El central es null, todos antes son ( y todos después son )
        if instruccion[len(instruccion)//2] != "null":
            return False
        else:
            if ")" in instruccion[0:len(instruccion)//2]:
                return False
            if "(" in instruccion[(len(instruccion)//2)+1 : -1]:
                return False
        # Si no pasó nada feo hasta acá, está bien escrito para el Caso 1a 
        return True
    
    # ============================================================
    # CASO 1b: El comando define una variable
    # ============================================================
    # Mismo razonamiento anterior con los paréntesis presentes
    elif principal == "defvar" and len(instruccion)%2 == 1:
        # Verificar si la instrucción tiene el formato correcto: 
        # defvar nombre_variable valor_variable, donde el nombre no puede coincidir con otra variable ni con una constante
        if len(instruccion) >= 5 and instruccion[i+1].isidentifier() and instruccion[i+2].isdigit() and instruccion[i+1] not in tabla_simbolos.keys() and instruccion[i+1] not in constantes:
            nombre_variable = instruccion[i+1]
            valor_inicial = int(instruccion[i+2])
            # Agregar el valor de la variable a la tabla de simbolos
            tabla_simbolos[nombre_variable] = valor_inicial  
        else:
            return False
        # Si no pasó nada feo hasta acá, está bien escrito para el Caso 1b
        return True
    
    # ============================================================
    # CASO 1c: El comando reasigna valor a una variable existente
    # ============================================================
    elif principal == "=" and len(instruccion)%2 == 1:
        # Verificar si la instrucción tiene el formato correcto:
        # = varname new_value, donde varname DEBE NECESARIAMENTE estar en la tabla de símbolos
        if len(instruccion) >= 5 and instruccion[i+2].isdigit() and instruccion[i+1] in tabla_simbolos.keys():
            # Actualizar el valor nuevo de la variable en la tabla de símbolos
            tabla_simbolos[instruccion[i+1]] = int(instruccion[i+2])
        else:
            return False
        # Si no pasó nada feo hasta acá, está bien escrito para el Caso 1c
        return True
    
    # ============================================================
    # CASO 1d: El comando involucra una unaria con un número
    # ============================================================
    # En este caso, los comandos siguen la forma (comando numero)
    # Por ende, siempre habrá un número par de tokens en la instrucción
    elif principal in ["move", "skip"] and len(instruccion)%2 == 0:
        # Verificar si la instrucción tiene el formato correcto:
        # move OR skip value, donde value debe ser un entero o ser una variable previamente asignada (en cuyo caso, ya es un entero)
        if len(instruccion) >= 4 and (instruccion[i+1].isdigit() or instruccion[i+1] in tabla_simbolos.keys()):
            return True
            
    # ============================================================
    # CASO 1e: El comando involucra una unaria con una orientación
    # ============================================================   
    # En este caso, los comandos siguen la forma (turn :param)
    # Por ende, siempre habrá un número par de tokens en la instrucción
    elif principal == "turn" and len(instruccion)%2 == 0:
        # Verificar si la instrucción tiene el formato correcto:
        # turn :param, donde :param debe ser un valor en una lista definida
        if len(instruccion) >= 4 and instruccion[i+1] in [":left", ":right", ":around"]:
            return True
     
    # ============================================================
    # CASO 1f: El comando involucra una unaria con una dirección
    # ============================================================
    # En este caso, los comandos siguen la forma (face :param)
    # Por ende, siempre habrá un número par de tokens en la instrucción
    elif principal == "face" and len(instruccion)%2 == 0:
        # Verificar si la instrucción tiene el formato correcto:
        # face :param, donde :param debe ser un valor en una lista definida
        if len(instruccion) >= 4 and instruccion[i+1] in [":north", ":south", ":east", ":west"]:
            return True
    
    # ============================================================
    # CASO 1g: El comando involucra una binaria
    # ============================================================
    # Siempre habrá un número impar de tokens en la instrucción
    elif principal in ["put", "pick"] and len(instruccion)%2 == 1:
        # Verificar si la instrucción tiene el formato correcto:
        # put OR pick X n, donde X es un objeto y n es un número entero
        if len(instruccion) >= 5 and instruccion[i+1] in [":balloons", ":chips"]:
            # El número n puede entrar directo o provenir de una variable ya asignada
            if instruccion[i+2].isdigit() or instruccion[i+2] in tabla_simbolos.keys():
                return True
        
    # ============================================================
    # CASO 1h: El comando involucra una operación especial
    # ============================================================
    # Verificar el uso correcto del move-dir, run-dirs, move-face
    elif principal in ["move-dir", "run-dirs", "move-face"]:
        
        # move-dir n D, donde n es número y D es un valor definido en una lista
        if principal == "move-dir":
            if (instruccion[i+1].isdigit() or instruccion[i+1] in tabla_simbolos.keys()) and instruccion[i+2] in [":front", ":right", ":left", ":back"]:
                return True
            
        # run-dirs Ds, donde Ds es una secuencia de orientaciones definidas en una lista
        elif principal == "run-dirs":
            # Extraemos las direcciones considerando la simetría de paréntesis
            # La última del listado estará en la posición -i (indexado de derecha a izquierda)
            direcciones = instruccion[i+1:-i]
            # Verificamos que todas las orientaciones sean válidas
            if all(dir in [":front", ":right", ":left", ":back"] for dir in direcciones):
                return True
        
        # move-face n O, donde n es un número y O es una dirección
        elif principal == "move-face":
            if (instruccion[i+1].isdigit() or instruccion[i+1] in tabla_simbolos.keys()) and instruccion[i+2] in [":north", ":south", ":west", ":east"]:
                return True
    
    
    # En caso de que no cumpla ninguno de estos casos se lanza la excepción
    else:
        raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un Comando.")
    # No tendría por qué llegar acá, pero esto evita inconsistencias
    return None


# ---------------------------------------------------------------------
# Parser de bloques de control
# ---------------------------------------------------------------------
def parse_control(instruccion, principal):
    # verificar los comandos de control
    
    # Si no se especifica lo contrario, se tiene un 0 porque no hay NOT
    comodin=0

    # ============================================================
    # CASO 2a: El bloque de control es un condicional (IF)
    # ============================================================
    if principal == "if":
        # Si sigue la estructura, el siguiente es un paréntesis y parsea la condición
        if instruccion[2] == "(":
            # Calcula la longitud esperada del condicional si es correcto
            longitud_condicional = 0
            if instruccion[3] == "facing?":
                longitud_condicional = 4
            elif instruccion[3] == "blocked?":
                longitud_condicional = 3
            elif instruccion[3] == "can-put?":
                longitud_condicional = 5
            elif instruccion[3] == "can-pick?":
                longitud_condicional = 5
            elif instruccion[3] == "can-move?":
                longitud_condicional = 4
            elif instruccion[3] == "iszero?":
                longitud_condicional = 4
            elif instruccion[3] == "not":
                comodin=2
        
                if instruccion[5] == "facing?":
                    longitud_condicional = 4
                elif instruccion[5] == "blocked?":
                    longitud_condicional = 3
                elif instruccion[5] == "can-put?":
                    longitud_condicional = 5
                elif instruccion[5] == "can-pick?":
                    longitud_condicional = 5
                elif instruccion[5] == "can-move?":
                    longitud_condicional = 4
                elif instruccion[5] == "iszero?":
                    longitud_condicional = 4
                else:
                    raise Exception(f"{instruccion[5]} no es valido como intrucción del condicional")
            
            else:
                    raise Exception(f"{instruccion[3]} no es valido como intrucción del condicional")  
                
            # Parsea el condicional específicamente
            
            parse_condition(instruccion[2+comodin:2+longitud_condicional+comodin])
            
            # Después del condicional, debe venir un comando o un bloque de control
        
            b1 = ["("]
            i = 2 + longitud_condicional + 1
            contador_parentesis = 1
            while contador_parentesis != 0:
                b1.append(instruccion[i])
                if instruccion[i] == "(":
                    contador_parentesis += 1
                if instruccion[i] == ")":
                    contador_parentesis -= 1
                i += 1
            # Parsear el primer bloque que se ha separado
            if b1[1] in comandos:
                parse_comando(b1, [])
            elif b1[1] in control:
                parse_control(b1, [])
            # Parsear el segundo bloque que se ha separado
            b2 = [instruccion[j] for j in range(i,len(instruccion)-1)]
            if b2[1] in comandos:
                parse_comando(b2, [])
            elif b2[1] in control:
                parse_control(b2, [])
                
            return True
        
        # Si no arranca en paréntesis después del if, se detiene el programa. Está mal
        else:
            raise Exception("La instrucción es un condicional. Se esperaba una condición después del IF.")
            
    # Si es una instrucción de bucle loop
    elif instruccion[1] == "loop":
        # Si sigue la estructura, el siguiente es un paréntesis y parsea la condición
        if instruccion[2] == "(":
                       # Calcula la longitud esperada del condicional si es correcto
            longitud_condicional = 0
            if instruccion[3] == "facing?":
                longitud_condicional = 4
            elif instruccion[3] == "blocked?":
                longitud_condicional = 3
            elif instruccion[3] == "can-put?":
                longitud_condicional = 5
            elif instruccion[3] == "can-pick?":
                longitud_condicional = 5
            elif instruccion[3] == "can-move?":
                longitud_condicional = 4
            elif instruccion[3] == "iszero?":
                longitud_condicional = 4
            elif instruccion[3] == "not":
                comodin=2
                
        
                if instruccion[5] == "facing?":
                    longitud_condicional = 4
                elif instruccion[5] == "blocked?":
                    longitud_condicional = 3
                elif instruccion[5] == "can-put?":
                    longitud_condicional = 5
                elif instruccion[5] == "can-pick?":
                    longitud_condicional = 5
                elif instruccion[5] == "can-move?":
                    longitud_condicional = 4
                elif instruccion[5] == "iszero?":
                    longitud_condicional = 4
                else:
                    raise Exception(f"{instruccion[5]} no es valido como intrucción dentro del loop")
            else:
                    raise Exception(f"{instruccion[3]} no es valido como intrucción dentro del loop")
            
            parametros=[]
            # Parsea el condicional específicamente
            parse_condition(instruccion[2+comodin:2+longitud_condicional+comodin], parametros)
            
            # Después del condicional, debe venir un comando o un bloque de control
            i = 2 + longitud_condicional
            # Parsear el bloque que se ha separado
            b = [instruccion[j] for j in range(i,len(instruccion)-1)]
            if b[1] in comandos:
                parse_comando(b, [])
            elif b[1] in control:
                parse_control(b, parametros)
        
            return True
        # Si no arranca en paréntesis después del if, se detiene el programa. Está mal
        else:
            raise Exception("La instrucción es un bucle. Se esperaba una condición después del LOOP.")

    # Si es una instrucción de repetición Repeat
    elif instruccion[1] == "repeat":
        # Si sigue la estructura, el siguiente es un número entero
        if instruccion[2].isdigit() or instruccion[2]in tabla_simbolos.keys() or instruccion[2]in parametros:
            # Le sigue ya sea un comando o un bloque de control
            b = [instruccion[k] for k in range(3, len(instruccion)-1)]
            # Parsear el bloque que se ha separado
            if b[1] in comandos:
                parse_comando(b, [])
            elif b[1] in control:
                parse_control(b, parametros)
        
            return True
        # Si no le sigue un número está mal
        else:
            raise Exception("La instrucción es un repeat. Se esperaba un número entero después del REPEAT.")

    return None


# ---------------------------------------------------------------------
# Parser de funciones y signaciones
# ---------------------------------------------------------------------
def parse_funciones(instruccion):
    # verificar las funciones
    
    #verifica si la funcion no existe 
    if instruccion[2] not in funcionesNumParametros.keys() and instruccion[3]=="(":
        instruccion_copia = copy.deepcopy(instruccion[3:])
        parametros = []
        x=0
        #verificar la correcta estructura de la funcion
        parentesis_abiertos = 0
         # Iterar sobre los tokens mientras que haya alguno sin procesar
        centinela = True
        while len(instruccion_copia) > 0 and centinela==True:
            # Revisar si inicia un paréntesis porque cada instrucción viene rodeada de uno
            token_actual = instruccion_copia.pop(0)
            
            if token_actual == "(":
                # Inicializar una lista para los tokens de un fragmento lógico
                fragmento_logico = []
                fragmento_logico.append(token_actual)
                parentesis_abiertos += 1
                
                # Repetir la extracción de paréntesis de inicio hasta llegar a una palabra reservada
                while instruccion_copia[0] == "(":
                    fragmento_logico.append(instruccion_copia.pop(0))
                    parentesis_abiertos += 1
                    
                # Obtener el cuerpo principal de la instrucción, el primero que no es (
                principal = instruccion_copia.pop(0)
                fragmento_logico.append(principal)
                
                # Recorrer la instrucción mientras que no se cierre del todo
                while parentesis_abiertos > 0:
                    token = instruccion_copia.pop(0)
                    # Ajustar el contador según los paréntesis que encuentre
                    if token == "(":
                        parentesis_abiertos += 1
                    if token == ")":
                        parentesis_abiertos -= 1
                    fragmento_logico.append(token)
        
                # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
                x+=1
                    
                if x==1:
                    if any(isinstance(item, str) for item in fragmento_logico[1:-1]):
                        for item in fragmento_logico[1:-1]:
                             parametros.append(item)
                             if instruccion[4]==")":
                                 parametros=[]
                elif x>1:
                    if fragmento_logico[1] in comandosfunciones:
                        parse_comando(fragmento_logico, parametros)
                    if fragmento_logico[1] in control:
                        parse_control(fragmento_logico, parametros)
            
        #Agregar la funcion a el diccionario
        funcionesNumParametros[instruccion[2]] = parametros
        return True
    
    #Hacer el caso donde la funcion ya existe
    elif instruccion[2] in funcionesNumParametros.keys():
        if len(instruccion) == 2+1+len(funcionesNumParametros[instruccion[1]]):
            x=2
            while instruccion[x]!=")":
                
                if not instruccion[x].isdigit() and instruccion[x] not in constantes:
                        raise Exception(f"Los parametros de {' '.join(instruccion)} no son correctos")
                x+=1
            return True       
                
            
    raise Exception(f"La instrucción {' '.join(instruccion)} no tiene la forma esperada")

    return None


# ---------------------------------------------------------------------
# Parser de condicionales
# ---------------------------------------------------------------------
def parse_condition(instruccion, parametros):
    # verificar las condiciones que se usan en la estrucutra de control if
    
    if instruccion[1] == "facing?" and len(instruccion) == 4 and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
        if instruccion[2] == "north" or instruccion[2] == "south" or instruccion[2] == "east" or instruccion[2] == "west":
            return True
    
    elif instruccion[1] == "blocked?" and len(instruccion) == 3 and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
        return True
    
    elif instruccion[1] == "can-put?" and len(instruccion) == 5:
        if instruccion[2] in ["chips", "balloons"] and (instruccion[3].isdigit() or instruccion[3]in tabla_simbolos.keys() or instruccion[3]in parametros) and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
            return True
    
    elif instruccion[1] == "can-pick?" and len(instruccion) == 5:
        if instruccion[2] in ["chips", "balloons"] and (instruccion[3].isdigit() or instruccion[3]in tabla_simbolos.keys() or instruccion[3]in parametros) and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
            return True
    
    elif instruccion[1] == "can-move?" and len(instruccion) == 4 and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
        if instruccion[2] in [":north", ":south", ":east", ":west"]:
            return True
    
    elif instruccion[1] == "iszero?" and len(instruccion) == 4 and instruccion[1] and instruccion[0] == "(" and instruccion[-1] == ")":
        if instruccion[2].isdigit() or instruccion[2]in tabla_simbolos.keys() or instruccion[2]in parametros:
            return True
    
    raise Exception(f"La instrucción {' '.join(instruccion)} no tiene la forma esperada")

    return False


# ---------------------------------------------------------------------
# Función para contar paréntesis
# ---------------------------------------------------------------------
def contar_parentesis(tokens):
    # Cuenta los paréntesis de apertura y de cierre
    parentesisIniciales = sum(1 for token in tokens if token == '(')
    parentesisFinales = sum(1 for token in tokens if token == ')')
    # Si no coinciden los ( y los ) o si no hay paréntesis, está mal
    if parentesisIniciales != parentesisFinales or parentesisIniciales == 0 or parentesisFinales == 0:
        raise Exception("La cantidad de paréntesis abiertos y cerrados no coincide.")
