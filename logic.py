# ============================================================
# PALABRAS RESERVADAS
# ============================================================

# Crear listas con caracteres reservados y palabras especiales del lenguaje
caracteres_reservados = ["(",")",":","-"]
comandos = ["defvar", "=", "move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
constantes = ["dim", "myxpos", "myypos", "mychips", "myballoons", "balloonshere", "chipshere", "spaces"]
control = ["if", "loop", "repeat", "defun"]
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
    tabla_simbolos[constante] = "0"
    
    
# ---------------------------------------------------------------------
# Inicio de las funciones del Parser
# ---------------------------------------------------------------------
def parse(lexer_result, esParteDeFuncion):
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
    intermedio = []
    parentesis_abiertos = 0

    # Iterar sobre los tokens mientras que haya alguno sin procesar
    # Cada vez que itere, necesariamente estará en otra instrucción
    while len(tokens) > 0:
        # Revisar si inicia con un paréntesis porque cada instrucción viene rodeada de uno
        if tokens[0]=="(" and tokens[1]==")" and len(tokens)==2:
            return True
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
            if principal==")":
                parentesis_abiertos = 0
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
            if fragmento_logico.index(principal) != 1 and principal in comandos:
                principales.pop(-1)
                separado = separar_bloque(fragmento_logico, principal)
                # Si es un bloque con varias instrucciones, está bien limitado con paréntesis
                # Separamos cada instrucción por separado
                for individual in separado[0]:
                    instrucciones.append(individual)
                for reservada in separado[1]:
                    principales.append(reservada)
            else:
                instrucciones.append(fragmento_logico)
        
    for k in range(len(instrucciones)):
        principal = principales[k]
        fragmento_logico = instrucciones[k]
        
        # Verificar si el cuerpo principal es un comando, una función o un bloque de control
        # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
        
        if not esParteDeFuncion:
            # ============================================================
            # CASO 1: El fragmento lógico es un COMANDO
            # ============================================================
            if principal in comandos:
                correctamente.append(parse_comando(fragmento_logico, principal))
            # ============================================================
            # CASO 2: El fragmento lógico es un BLOQUE DE CONTROL
            # ============================================================
            elif principal in control and principal != "defun":
                correctamente.append(parse_control(fragmento_logico, principal))
            # ============================================================
            # CASO 3: El fragmento lógico es una SIGNACIÓN DE FUNCIÓN
            # ============================================================
            elif principal == "defun":
                correctamente.append(parse_funciones(fragmento_logico, principal))
            # ============================================================
            # CASO 4: El fragmento lógico es una FUNCIÓN DECLARADA
            # ============================================================
            elif principal in funcionesNumParametros.keys():
                correctamente.append(parse_funciones(fragmento_logico, principal))
            # ============================================================
            # CASO 5: El principal no corresponde a ninguna instrucción
            # ============================================================
            # Se lanza una excepción y se detiene la ejecución en este punto
            elif principal==")":
                correctamente.append(True)
            else:
                raise Exception(f"{fragmento_logico} no se reconoce este tipo de instrucción")  
        
        #Uso de nuevo el parser pero para las intrucciones que estan dentro de una estructura de control
        elif esParteDeFuncion:
            # ============================================================
            # CASO 1: El fragmento lógico es un COMANDO
            # ============================================================
            if principal in comandos:
                intermedio.append(parse_comando(fragmento_logico, principal))

            # ============================================================
            # CASO 1h: El comando involucra recursion 
            # ============================================================
            elif principal in funcionesNumParametros.keys():
                intermedio.append(parse_funciones(fragmento_logico, principal))
                
            # ============================================================
            # CASO 1h: El comando involucra estructuras de control 
            # ============================================================
            elif principal in ["if", "loop", "repeat"]:
                intermedio.append(parse_control(fragmento_logico, principal))
            
            elif principal==")":
                correctamente.append(True)
                
            else:
                raise Exception("La instrucción " + ' '.join(fragmento_logico) + " no tiene la forma esperada.")

    # Estará bien escrito si no hay Falsos en las listas
    bien_escrito = False not in correctamente and False not in intermedio
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
        if (len(instruccion) >= 5 and instruccion[i+1].isidentifier() and instruccion[i+1] not in tabla_simbolos.keys() and instruccion[i+1] not in constantes
            and instruccion[i+2] not in caracteres_reservados and instruccion[i+2] not in comandos and instruccion[i+2] not in control and instruccion[i+2] not in condition):
            nombre_variable = instruccion[i+1]
            valor_inicial = instruccion[i+2]

            # Agregar el valor de la variable a la tabla de simbolos si no es reservada/especial ni igual al nombre de una función
            if (nombre_variable not in caracteres_reservados and nombre_variable not in comandos
                and nombre_variable not in control and nombre_variable not in constantes
                and nombre_variable not in condition and nombre_variable not in funcionesNumParametros.keys()):
                tabla_simbolos[nombre_variable] = valor_inicial  
            else:
                return False
                
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
        if (len(instruccion) >= 5 and instruccion[i+1] in tabla_simbolos.keys()
            and instruccion[i+2] not in caracteres_reservados and instruccion[i+2] not in comandos and instruccion[i+2] not in control and instruccion[i+2] not in condition):
            # Actualizar el valor nuevo de la variable en la tabla de símbolos
            tabla_simbolos[instruccion[i+1]] = instruccion[i+2]
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
        if len(instruccion) >= 4 and (instruccion[i+1].isdigit() or tabla_simbolos[instruccion[i+1]].isdigit() or tabla_simbolos[instruccion[i+1]] == "Temporal"):
            return True
            
    # ============================================================
    # CASO 1e: El comando involucra una unaria con una orientación
    # ============================================================   
    # En este caso, los comandos siguen la forma (turn :param)
    # Por ende, siempre habrá un número par de tokens en la instrucción
    elif principal == "turn" and len(instruccion)%2 == 0:
        # Verificar si la instrucción tiene el formato correcto:
        # turn :param, donde :param debe ser un valor en una lista definida
        if len(instruccion) >= 4 and (instruccion[i+1] in [":left", ":right", ":around"] or tabla_simbolos[instruccion[i+1]] in [":left", ":right", ":around"] or tabla_simbolos[instruccion[i+1]] == "Temporal"):
            return True
     
    # ============================================================
    # CASO 1f: El comando involucra una unaria con una dirección
    # ============================================================
    # En este caso, los comandos siguen la forma (face :param)
    # Por ende, siempre habrá un número par de tokens en la instrucción
    elif principal == "face" and len(instruccion)%2 == 0:
        # Verificar si la instrucción tiene el formato correcto:
        # face :param, donde :param debe ser un valor en una lista definida
        if len(instruccion) >= 4 and (instruccion[i+1] in [":north", ":south", ":east", ":west"] or tabla_simbolos[instruccion[i+1]] in [":north", ":south", ":east", ":west"] or tabla_simbolos[instruccion[i+1]] == "Temporal"):
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
            x=instruccion[i+2]
            if  x.isdigit() or tabla_simbolos[instruccion[i+2]].isdigit() or tabla_simbolos[instruccion[i+2]] == "Temporal":
                return True
        
    # ============================================================
    # CASO 1h: El comando involucra una operación especial
    # ============================================================
    # Verificar el uso correcto del move-dir, run-dirs, move-face
    elif principal in ["move-dir", "run-dirs", "move-face"]:
        
        # move-dir n D, donde n es número y D es un valor definido en una lista
        if principal == "move-dir":
            if ((instruccion[i+1].isdigit() or tabla_simbolos[instruccion[i+1]].isdigit() or tabla_simbolos[instruccion[i+1]] == "Temporal") and 
            (instruccion[i+2] in [":front", ":right", ":left", ":back"] or tabla_simbolos[instruccion[i+2]] in [":front", ":right", ":left", ":back", "Temporal"])):
                return True
            
        # run-dirs Ds, donde Ds es una secuencia de orientaciones definidas en una lista
        elif principal == "run-dirs":
            # Extraemos las direcciones considerando la simetría de paréntesis
            # La última del listado estará en la posición -i (indexado de derecha a izquierda)
            direcciones = instruccion[i+1:-i]
            # No puede ser un listado vacío de direcciones
            if len(direcciones) == 0:
                return False
            # Verificamos que todas las orientaciones sean válidas

            for direccion in direcciones:
                if direccion not in [":front", ":right", ":left", ":back"]:
                        if tabla_simbolos.get(direccion) not in [":front", ":right", ":left", ":back", "Temporal"]:
                            raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un Comando.")
            return True


        
        # move-face n O, donde n es un número y O es una dirección
        elif principal == "move-face":
            if ((instruccion[i+1].isdigit() or tabla_simbolos[instruccion[i+1]].isdigit() or tabla_simbolos[instruccion[i+1]] == "Temporal") and 
            (instruccion[i+2] in [":north", ":south", ":west", ":east", "Temporal"] or tabla_simbolos[instruccion[i+2]] in [":north", ":south", ":west", ":east"])):
                return True

    
    # En caso de que no cumpla ninguno de estos casos se lanza la excepción
    else:
        raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un Comando.")
    # No tendría por qué llegar acá, pero esto evita inconsistencias
    return False


# ---------------------------------------------------------------------
# Parser de bloques de control
# ---------------------------------------------------------------------
def parse_control(instruccion, principal):
    # Identificar la posición en la que empieza el principal
    i = instruccion.index(principal)
    
    if i != 1:
        # Por la estructura del lenguaje, es válido eliminar lo externo
        instruccion.pop(0)
        instruccion.pop(-1)
        # Se manda recursivamente a que parsee el interior del bloque
        return parse(instruccion, False)
    
    else:
        # ============================================================
        # CASO 2a: El bloque de control es un condicional (IF)
        # ============================================================
        if principal == "if":
            count_parentheses = 0
            condition = []
            b1 = []
            b2 = []
            ins=[]
    
            lst= instruccion
            
            #ya se sabe que es un if por lo que se empieza a comprobar que siga la estructura estrablecida
            
            for elem in lst[2:-1]:
                
                #aqui empezamos a contar parentesis para poder divir las tres partes que tiene un if (Condicion, B1 y B2)
                if elem == "(":
                    count_parentheses += 1
                elif elem == ")":
                    count_parentheses -= 1
                ins.append(elem)
                if count_parentheses == 0:
                    # Primer elemento después del paréntesis cerrado es la condición
                    if not condition:
                        condition = elem
                        bien = parse_condition(eliminar_parentesis_extra(ins), [])
                        if not bien:
                            return False
                        #se inicializa nuevamente la lista para dividir los pedazos de el condicional
                        ins=[]
                    # Elementos entre el primer y segundo paréntesis cerrado son B1
                    elif not b1:
                        b1 = ins
                        bien = parse(b1, True)
                        if not bien:
                            return False
                        #se inicializa nuevamente la lista para dividir los pedazos de el condicional
                        ins=[]
                    # Elementos después del segundo paréntesis cerrado son B2
                    elif not b2:
                        b2 = ins
                        bien = parse(b2, True)
                        if not bien:
                            return False
                        #se inicializa nuevamente la lista para dividir los pedazos de el condicional
                        ins=[]
                    #Si siguen habiendo elementos despues de esto es que hay un error
                    else:
                        raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un condicional.")
                #Si siguen habiendo elementos despues de esto es que hay un error
                elif b2:
                    raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un condicional.")
            
            if not condition or not b1 or not b2:
                    raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un condicional.")
        
            return True
        # ============================================================
        # CASO 2b: Repeat: (loop condition B):
        # ============================================================
        if principal == "loop":
            count_parentheses = 0
            condition = []
            b1 = []
            ins=[]
            lst= instruccion
            for elem in lst[2:-1]:
                if elem == "(":
                    count_parentheses += 1
                elif elem == ")":
                    count_parentheses -= 1
                ins.append(elem)
                if count_parentheses == 0:
                    # Primer elemento después del paréntesis cerrado es la condición
                    if not condition:
                        condition = elem
                        parse_condition(eliminar_parentesis_extra(ins), [])
                        ins=[]
                    # Los siguientes elementos deben de ser un bloque de comandos 
                    elif not b1:
                        b1 = ins
                        parse(b1, True)
                        ins=[]
                    #Si hay mas elementos depues de esto es que se trata de un error
                    else:
                        raise Exception("No se cumple con la estructura del loop, pues se tienen mas bloques de commandos de los que se deberia.")
           
            if not condition or not b1:
                raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un condicional.")
        
            return True
        # ============================================================
        # CASO 2c: Repeat: (repeat n B):
        # ============================================================
           
        if principal == "repeat":
            b1 = []
            ins=[]
            count_parentheses=0
            #sabes que el repeat tiene que tener una variable despues de la palabra repeat 
            if instruccion[2].isdigit()  or instruccion[2] in constantes or instruccion[2] in tabla_simbolos.keys():
                #con este condicional solo nos aseguramos que esta intruccion se cierre con parentesis para evitar errores 
                if instruccion[-1] ==")":
                    #Aqui vamos a iterar donde en teoria deberia encontrarse ubicado el bloque de comandos 
                    for elem in instruccion[3:-1]:
                        if elem == "(":
                            count_parentheses += 1
                        elif elem == ")":
                            count_parentheses -= 1
                        ins.append(elem)
                        #Aqui entramos a analizar los diferentes comandos dentro del bloque
                        if count_parentheses == 0:
                            if not b1:
                                b1 = ins
                                parse(b1, True)
                            #Solo hay un bloque de comandos, si hay mas es por que esta mal
                            else:
                                raise Exception("No se cumple con la estructura del repeat, pues se tienen mas bloques de commandos de los que se deberia.")
                    if not b1:
                        raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para un condicional.")
                
                    return True
        
        
        raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada para una estructura de control.")
      
    return False


# ---------------------------------------------------------------------
# Parser de funciones y signaciones
# ---------------------------------------------------------------------
def parse_funciones(instruccion, principal):
    # Identificar la posición en la que empieza el principal
    i = instruccion.index(principal)
    
    if i != 1:
        # Por la estructura del lenguaje, es válido eliminar lo externo
        instruccion.pop(0)
        instruccion.pop(-1)
        # Se manda recursivamente a que parsee el interior del bloque
        return parse(instruccion, False)
    
    # ============================================================
    # CASO 3a: La signación de una función no existente
    # ============================================================
    # El principal es defun y el siguiente token es el nombre de la función
    if principal == "defun" and instruccion[i+1] not in funcionesNumParametros.keys():   
        # Como no existe en el diccionario, se agrega
        nombre_funcion = instruccion[i+1]
        # No puede ser palabra o símbolo especial/reservado ni constante ni variable
        if (nombre_funcion not in caracteres_reservados and nombre_funcion not in comandos
            and nombre_funcion not in control and nombre_funcion not in constantes
            and nombre_funcion not in condition and nombre_funcion not in tabla_simbolos.keys()):
            # Si es correcto, el siguiente token debería ser un (
            if instruccion[i+2] != "(":
                return False
            else:
                # Empieza a revisar el listado de parámetros que inicia desde el (
                parametros = []
                contador_params = 3
                # Los agrega a un listado de parámetros contemplando que acaban con )
                while instruccion[i + contador_params] != ")":
                    parametros.append(instruccion[i + contador_params])
                    contador_params += 1
                # Verifica la terminación del listado de parámetros
                if instruccion[i + contador_params] != ")":
                    return False
                else:
                    # Agrega temporalmente los parámetros a las variables
                    for p in parametros:
                        if p not in tabla_simbolos.keys():
                            tabla_simbolos[p] = "Temporal"
                    # Si los parámetros son correctos, revisa la secuencia de comandos
                    # Se agrega para asegurar la Recursión en caso de que se llame a sí misma en su secuencia
                    funcionesNumParametros[nombre_funcion] = parametros
                    secuencia_comandos = instruccion[i + contador_params + 1: -1]
                    secuencia_correcta = parse(secuencia_comandos,False)
                    # Si los parámetros no son correctos, quita la función
                    if not secuencia_correcta:
                        funcionesNumParametros.pop(nombre_funcion)
                        return False
                    # Elimina los parámetros agregados temporalmente
                    for p in parametros:
                        if tabla_simbolos[p] == "Temporal":
                            tabla_simbolos.pop(p)
                # Si todo salió bien hasta acá, la signación es correcta
                return True
        
    # ============================================================
    # CASO 3b: La signación de una función ya existente
    # ============================================================
    # El principal es defun y el siguiente token es el nombre de la función
    elif principal == "defun" and instruccion[i+1] in funcionesNumParametros.keys():
        # No se puede reescribir una función. Siempre deben tener nombres diferentes
        return False
    
    # ============================================================
    # CASO 4a: El llamado de una función ya existente
    # ============================================================
    # El principal llegó acá porque no es una palabra reservada
    # El principal DEBE NECESARIAMENTE estar en el diccionario de funciones
    elif principal in funcionesNumParametros.keys():
        # Al haber sido ya declarada, esto garantiza la Recursión
        parametros = []
        # El nombre debe estar seguido de los parámetros
        k = 1
        while instruccion[i+k] != ")":
            parametros.append(instruccion[i+k])
            k += 1
        # Si el número de parámetros en la invocación coincide con los de la signación
        numparametros=len(funcionesNumParametros[principal])
        if not funcionesNumParametros[principal]:
            numparametros=0
            
        if len(parametros) == numparametros:
            # Revisar que los parámetros que llegan no sean reservados (a menos que sean constantes o variables)
            # Los parámetros sólo pueden ser variables guardadas, constantes o números enteros
            for param in parametros:
                if (param not in caracteres_reservados and param not in comandos
                    and param not in control and param not in condition and param not in funcionesNumParametros.keys()
                    and (param in tabla_simbolos.keys() or param in constantes or param.isdigit()
                         or param in [":left", ":right", ":front", ":back", ":around"] 
                         or param in [":north", ":south", ":west", ":east"])): 
                    return True
                # Si está en alguna lista reservada, está mal
                else:
                    raise Exception("La instrucción " + ' '.join(instruccion) + " esta en una lista reservada.")
            # Si no tiene parámetros, prosigue
            return True
        # Si no coinciden los parámetros, está mal
        else:
            raise Exception("La instrucción " + ' '.join(instruccion) + " no coincide con los parametros de la funcion.")
                    
    
    # ============================================================
    # CASO 4b: El llamado de una función no existente
    # ============================================================
    # El principal llegó acá porque no es una palabra reservada
    # El principal no se encuentra en el diccionario de funciones
    elif principal not in funcionesNumParametros.keys():
        # Por chequear, tampoco se encuentra en ningún otro listado
        if (principal not in caracteres_reservados and principal not in comandos
            and principal not in control and principal not in constantes
            and principal not in condition and principal not in tabla_simbolos.keys()):
            # Si pasó por los anteriores filtros, está mal
            print("Esta función no está creada")
            return False
    
    # En caso de que no cumpla ninguno de estos casos se lanza la excepción
    else:        
        raise Exception(f"La instrucción {' '.join(instruccion)} no tiene la forma esperada")
    # No tendría por qué llegar hasta acá, pero así se evitan inconsistencias
    return False


# ---------------------------------------------------------------------
# Eliminar parentesis exteriores para el parse condirion
# ---------------------------------------------------------------------
def eliminar_parentesis_extra(lista):
    contar=0
    for caracter in lista:
        if caracter == "(":
            contar+=1
        else:
           break
    if contar>1:
        return lista[contar-1:-contar+1]
    else:
        return lista
    
    
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
    
    elif instruccion[1] == "not" and instruccion[0] == "(" and instruccion[-1] == ")":
        instruccion.pop(0)
        instruccion.pop(0)
        instruccion.pop(-1)
        return parse_condition(eliminar_parentesis_extra(instruccion), parametros)
        
    
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


# ---------------------------------------------------------------------
# Función para separar bloques en instrucciones individuales
# ---------------------------------------------------------------------
def separar_bloque(bloque, principal):
    # Importa que haya una palabra reservada precedida de un (
    indice = 0
    individuales = []
    principales = []
    while len(bloque) > 0:
        # Manejo en caso que el bloque inicie con un comando
        if bloque[indice] == "(" and (bloque[indice + 1] in comandos or bloque[indice + 1] != "("):
            comando = []
            principales.append(bloque[indice + 1])
            # Agregar tokens de una instrucción hasta llegar al cierre
            while bloque[indice] != ")":
                comando.append(bloque.pop(indice))
            # Agregar el cierre de la instrucción
            comando.append(bloque.pop(indice))
            # Agregar el comando cerrado a la lista de instrucciones separadas
            individuales.append(comando)
        else:
            bloque.pop(indice)
        
    return individuales, principales
