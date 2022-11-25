import io

def escribirArchivo(nombreArchivo, lineasEscribir):
    
    archivoEscribir = open(nombreArchivo,"w")
    for linea in lineasEscribir:
        archivoEscribir.write(linea[0]+"\n")
        archivoEscribir.write(linea[1]+"\n")

    archivoEscribir.close()

def leerArchivo(nombreArchivo):

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()
   
    for linea in lineasLeidas:
        print(linea.split(","))
    archivoLeer.close()

    return lineasLeidas

def compruebaCredenciales(nombreArchivo, user, password):

    credencialesValidas = False

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()

    for numLinea in range(len(lineasLeidas)):

        if user == lineasLeidas[numLinea][:-1]:
            if (numLinea +1)<= len(lineasLeidas) and password == lineasLeidas[numLinea+1][:-1]:
                credencialesValidas = True
    
    return credencialesValidas
            




nombreArchivo = "bbddCredenciales.txt"

lineasEscribir = []
lineasEscribir.append(("EnriqueAP6","010203"))
lineasEscribir.append(("eap_6","102030"))
lineasEscribir.append(("efjvdj","odiewsnjd"))
lineasEscribir.append(("user","password"))

escribirArchivo(nombreArchivo, lineasEscribir)
contenidoArchivo = leerArchivo(nombreArchivo)

print(compruebaCredenciales(nombreArchivo,"eap_6","102030"))
print(compruebaCredenciales(nombreArchivo,"eap_6","password"))
print(compruebaCredenciales(nombreArchivo,"user","password"))


