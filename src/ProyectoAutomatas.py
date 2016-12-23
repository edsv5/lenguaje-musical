#Eduardo Solorzano V. B36848
#Jason Anchia V. B30390
#

import sys

####################Analizador lexico (lexer)####################

#VARIABLES GLOBALES (aqui guardamos valores globales para poder modificarlos con los modos)

octavaGlobal = 4
duracionGlobal = 1
nombreArchivo = sys.argv[1] + ".mid"

#TOKENS

tokens = ['NOTA','TIEMPO', 'DURACION', 'MODOOCTAVA', 'MODODURACION', 'MODOTEMPO', 'INSTRUMENTO', 'CAMBIOINSTRUMENTO', 'MOD']

literals = ['-', '(' , ')', 't', 'd', 'o', '|', ',', 'x'] #El 'x' es para debuggear

t_ignore  = ' \t' #Que ignore los espacios
t_MOD = 'mod'
t_INSTRUMENTO = 'instrumento'

#Este token es para cambiar el instrumento a traves de un programChange
#program es el instrumento, los instrumentos que seran incluidos son los siguientes:
#
#1: Acoustic piano
#5: Electric piano 1
#11: Music box
#12: Vibrafono
#21: Reed organ
#22: Accordion
#23: Harmonica
#24: Tango Accordion
#25: Acoustic guitar (nylon)
#27: Jazz guitar
#34: Electric bass (finger)
#41: Violin
#50: String ensemble 2
#
#Se aplica el siguiente metodo con el t.value que devuelva
#
#   MyMIDI.addProgramChange(track, channel, 0, instrumento)
#
#El cambio de instrumento se hace de una manera global, es decir, se hace el cambio de instrumento
#a partir del tiempo 0 predeterminadamente.
#El formato para cambiar el instrumento es: instrumento(instrumentoQueSeQuiereAsignar)

def t_CAMBIOINSTRUMENTO(t):
    r'(piano|epian|mbox|vib|reedorg|accordion|harm|tacc|acguitar|jazzguitar|ebass|violin|strensemble)'
    if 'piano' in t.value:
        t.value = 1
    elif 'epian' in t.value:
        t.value = 5
    elif 'mbox' in t.value:
        t.value = 11
    elif 'vib' in t.value:
        t.value = 12
    elif 'reedorg' in t.value:
        t.value = 21
    elif 'accordion' in t.value:
        t.value = 22
    elif 'harm' in t.value:
        t.value = 23
    elif 'tacc' in t.value:
        t.value = 24
    elif 'acguitar' in t.value:
        t.value = 25
    elif 'jazzguitar' in t.value:
        t.value = 27
    elif 'ebass' in t.value:
        t.value = 34
    elif 'violin' in t.value:
        t.value = 41
    elif 'strensemble' in t.value:
        t.value = 50
    return t

#Esto cambia el modo de duracion de las notas con la palabra mod, seguida de la duracion que se quiere asignar
#Esta asignacion se hace en el analisis lexico ya que no se vio la necesidad de hacerlo en el sintactico

def t_MODODURACION(t):
    r'dur(RED|B|N|C|SC)'
    global duracionGlobal
    if 'RED' in t.value:
        duracionGlobal = 4
    elif 'B' in t.value:
        duracionGlobal = 2
    elif 'N'in t.value:
        duracionGlobal = 1
    elif 'C'in t.value:
        duracionGlobal = 0.5
    elif 'SC'in t.value:
        duracionGlobal = 0.25
    return t


#Esto es para cambiar el tempo GLOBAL (desde el tiempo 0) de la pieza

def t_MODOTEMPO(t):
    r'tempo \( [1-2]?[0-9][0-9] \) '
    t.value = int(filter(str.isdigit, t.value))
    return t

#Esto cambia la octava de las notas subsiguientes

def t_MODOOCTAVA(t):
    r'oct[1-7]'
    global octavaGlobal
    octavaGlobal = int(filter(str.isdigit, t.value)) #Asigna el numero extraido del token a la octavaGlobal
    return t

#El tiempo en el que la nota va a estar insertada, toma el numero y lo convierte a
#float para poder meter notas con una duracion menor a 1 (corcheas, semicorcheas)

def t_TIEMPO(t):
    r'[0-9]+\.?[0-9]*'
    t.value = float(t.value)
    return t

#Este metodo asigna el numero de duracion de las notas en el analisis lexico
#Los tiempos son los siguientes segun los tokens:
#
#   red: redonda (4 tiempos)
#   b: blanca (2 tiempos)
#   n: negra (1 tiempo)
#   c: corchea (0.5 tiempos)
#   sc: semicorchea (0.25 tiempos)
#
#Las notas permiten ser ingresadas con puntillo o sin puntillo

def t_DURACION(t):
    r'(red|b|n|c|sc)(\.)?'
    tiempoNota = 0
    if 'red' in t.value: #redonda
        tiempoNota = 4
    elif 'b' in t.value: #blanca
        tiempoNota = 2
    elif 'n' in t.value: #negra
        tiempoNota = 1
    elif 'c' in t.value: #corchea
        tiempoNota = 0.5
    elif 'sc' in t.value: #semicorchea
        tiempoNota = 0.25

    if '.' in t.value: #En el caso de que sea una nota con puntillo, le suma la mitad del tiempo de la nota
        tiempoNota = tiempoNota + tiempoNota*0.5

    t.value = tiempoNota
    return t


#Cada vez que encuentra una nota identifica cual nota es y
#le asigna su numero midi para agregarla al archivo
#
#Las notas que se ingresen sin octava que le siga, seran colocadas en la octava global.
#La octavaGlobal por default es la octava 4.
#
#Segun la octava que encuentre en la produccion, suma o resta lo que necesite
#para estar en la octava especificada, el proyecto va a incluir
#notas desde la octava 1 hasta la 8.
#
#En este metodo, primero se iguala la octavaGlobal a la octavaLocal, si hay algun cambio
#especificado en el token, la octavaLocal se vuelve a cambiar, si no lo hay, la octavaLocal queda
#con el valor de la octavaGlobal, despues para dar la nota, se hace esta operacion:
#
#       nota = nota + 12*octavaLocal
#
#De esta manera, se le suma a la nota en la octava 0, la cantidad de octavas que le corresponde
#
#Notas:
#
#   - Es permitido utilizar un mi# ya que este es el equivalente a un fa natural al
#   aumentar un semitono en la nota mi. Ademas de eso, es permitido usar un dob,
#   que es equivalente a si natural en la octava superior. Tambien se puede usar un si# para referirse a un
#   do natural en la octava anterior
#
#   -Las notas deben escribirse en el orden:
#
#       NOTA ACCIDENTE OCTAVA (todo seguido, sin espacios)
#
#   - Si el usuario escribe todas sus notas sin declarar nunca la octava global, estas
#   quedaran por default en la octava 4.
#   - Una serie de notas puede ir acompanadas por un | antes o despues de la nota
#   esto es para que el usuario pueda anadir compases a su partitura y asi, que queden mas organizadas
#   las notas.
#   - Una serie de notas debe estar agrupada por -'s o |'s

def t_NOTA(t):

    r'(do|re|mi|fa|sol|la|si)(\#|b)?([1-8])?'

    #Se mantiene una variable global para la octava y se usa para calcular la octava local que
    #se le suma al valor midi si el usuario no especifico la octava en el token

    global octavaGlobal #Se adquiere el valor de la octavaGlobal

    #Se inicializa la octavaLocal con el valor de la octavaGlobal
    #en el caso de que no se ingresen octavas a la nota

    octavaLocal = octavaGlobal

    #Se inicializa la variable nota que va a almacenar un numero que se asignara
    #dependiendo de la nota que se encuentre el lexer

    nota = 0

    #Identifica la nota y le asigna un numero

    if 'do' in t.value:
        nota = 0
    elif 're' in t.value:
        nota = 2
    elif 'mi' in t.value:
        nota = 4
    elif 'fa' in t.value:
        nota = 5
    elif 'sol' in t.value:
        nota = 7
    elif 'la' in t.value:
        nota = 9
    elif 'si' in t.value:
        nota = 11

    #Si hay #'s (sostenidos) aumenta un semitono (aumenta 1 en el numero midi)
    #Si hay b's (bemoles) decrementa un semitono (decrementa 1 en el numero midi)

    if '#' in t.value:
        nota += 1
    elif 'b' in t.value:
        nota -= 1

    #Se asigna el numero de octava dado el numero que se ingreso (si es que se ingreso)

    if '1' in t.value:
        octavaLocal = 1
    elif '2' in t.value:
        octavaLocal = 2
    elif '3' in t.value:
        octavaLocal = 3
    elif '4' in t.value:
        octavaLocal = 4
    elif '5' in t.value:
        octavaLocal = 5
    elif '6' in t.value:
        octavaLocal = 6
    elif '7' in t.value:
        octavaLocal = 7
    elif '8' in t.value:
        octavaLocal = 8

    #Despues deja la nota final como la suma del numero que se le asigno mas
    #su octavaLocal multiplicada por 12 (12 notas por octava deben ser sumadas)

    t.value = nota + 12*octavaLocal

    return t


def t_newline(t): #Para llevar control del numero de lineas
    r'\n'
    t.lexer.lineno += t.value.count("\n")

# Manejo de errores

def t_error(t):
    print "Caracter no permitido: '", t.value[0], "'", 'en la linea', t.lineno
    t.lexer.skip(1)

#Montar el analizador lexico

import ply.lex as lex
lex.lex()

####################Analisis sintactico (parsing rules)####################

#Reglas (aqui se definen las producciones y que hacer cada vez que encuentra una)

#Esta produccion mete la nota especificada en el metodo junto con su tiempo respectivo
#Es importante tener en cuenta que para meter una nota corchea, se debe meter 0.5 tiempos despues.
#Es decir, para meter una serie de corcheas seria: do t0 dc - re t0.5 dc - mi t1 dc.
#Igual con las semicorcheas, solo con que cada nota metida en intervalos de 0.25, es decir, 1/4 de tiempo.
#Cada nota se puede separar tanto con un '-' como con un '|', esto le da la libertad al usuario
#de expresar su musica como una serie de notas o una serie de compases compuestos de notas.
#Se supone que el simbolo '|' sea usado como separador de compases, no obstante, esto no tiene
#efecto en el audio final, sin embargo, deberia ser usado para dar mas orden al codigo.
#
#   p[1]: nota
#   p[3]: tiempo
#   p[5]: duracion


def p_notasConDuracion(p):
    '''S : NOTA  't' TIEMPO 'd' DURACION '-' S
    | NOTA  't' TIEMPO 'd' DURACION '|' S
    | NOTA 't' TIEMPO 'd' DURACION'''
    MyMIDI.addNote(0,channel,p[1],p[3],p[5],volume)


#Este es el caso en el que encuentre notas cuya duracion no sea espeficada, en
#cuyo caso, le asignara a la nota la duracionGlobal ya declarada.
#La duracion global por default es 1 (negra), pero es posible cambiarla cambiando de modo

def p_notasSinDuracion(p):

    '''S : NOTA 't' TIEMPO '-' S
    | NOTA 't' TIEMPO '|' S
    | NOTA 't' TIEMPO'''
    MyMIDI.addNote(0,channel,p[1],p[3],duracionGlobal,volume)


#Esta produccion es para poder cambiar de octava, ej: si se ingresa un oct6, se cambia a la octava 6
#y todas las notas subsiguientes son escritas en esa octava (a menos que se indique lo contrario).
#Es importante mencionar que la octavaGlobal se cambia en el analisis lexico una vez que encuentra el token
#con su respectiva octava

def p_cambioOctava(p):
    '''S : MOD '(' MODOOCTAVA ')' '-' S
    | MOD '(' MODOOCTAVA ')' '|' S
    | MOD '(' MODOOCTAVA ')' '''

#Esta produccion es para cambiar la duracion de las notas subsiguientes

def p_cambioDuracion(p):
    '''S : MOD '(' MODODURACION ')' '-' S
    | MOD '(' MODODURACION ')' '|' S
    | MOD '(' MODODURACION ')' '''

#Esta produccion es para cambiar de instrumento, ya sea en una linea o en medio de notas o compases
#Por ahora, este cambio de instrumento se hace de una manera GLOBAL, es decir, en el tiempo 0
#Es decir, si se ingresa un cambio de instrumento en cualquier parte de la pieza, este sera cambiando
#en todos los compases.

def p_cambioInstrumento(p):
    '''S : INSTRUMENTO '(' CAMBIOINSTRUMENTO ')' '-' S
    | INSTRUMENTO '(' CAMBIOINSTRUMENTO ')' '|' S
    | INSTRUMENTO '(' CAMBIOINSTRUMENTO ')' '''

    MyMIDI.addProgramChange(track, channel, 0, p[3])

#Esta produccion es para poder cambiar el tempo de la cancion.
#Un cambio de tempo debe ser ingresado con el siguiente formato:
#
#   tempo(tempoDeseado)
#
#Por ejemplo para cambiar el tempo a 50 bpm se deberia ingresar:
#
#   tempo(50)
#
#La biblioteca no es capaz de manejar una cancion con tempos en diferentes tiempos de una manera
#no atroz, por lo tanto, si el usuario cambia el tempo en cualquier parte de la pieza, este sera cambiado
#para toda la pieza. Esto ayuda tambien a mantener el formato minimalista de las piezas que se quieren lograr
#escribir.
#
#Si el usuario ingresa varios cambios de tempo a lo largo de la pieza, esta quedara con el que este puesto
#de primero en la pieza de arriba a abajo.

def p_cambioTempo(p):
    '''S : MODOTEMPO  '-' S
    | MODOTEMPO  '|' S
    | MODOTEMPO '''

    MyMIDI.addTempo(track,0,p[1]) #Agrega el tempo especificado en el tiempo 0

#Esta produccion es para que el usuario pueda meter divisiones de compases antes
#de ingresar la nota

def p_separacionCompas(p):
    '''S : '|' S '''

#Esta produccion es en caso de que encuentre lineas vacias, lo cual debe ser permitido porque nuestro lenguaje
#es maravilloso y las lineas vacias estan bienvenidas en el
def p_vacio(p):
    '''S : '''

#MANEJO DE ERRORES

def p_error(p):
    print "Error sintactico en '", p.value, "'" , 'en la linea', p.lineno

#Montar el analizador sintactico

import ply.yacc as yacc
yacc.yacc()

####################CORRER EL PARSER########################

#Importa la biblioteca para crear archivos midi

from midiutil.MidiFile import MIDIFile

# Crea un archivo midi con 1 track

MyMIDI = MIDIFile(1)

# Los tracks empiezan a contarse desde 0, Los tiempos se cuentan en beats
track = 0
time = 0
channel = 0
# Anade el nombre del track y el tempo
MyMIDI.addTrackName(track,time,"Trackcero")
volume = 100

with open(sys.argv[1]) as f: #Parsea el archivo linea por linea
    for line in f.readlines():
        yacc.parse(line)

#Despues de haber hecho el analisis sintactico del archivo, crea el output

binfile = open(nombreArchivo, 'wb')
MyMIDI.writeFile(binfile)
binfile.close()
