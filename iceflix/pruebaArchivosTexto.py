import io

def introducirDatoArchivo(nombreArchivo, lineaEscribir):
    
    archivoEscribir = open(nombreArchivo,"a")
    archivoEscribir.write(lineaEscribir+"\n")
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

introducirDatoArchivo(nombreArchivo, "EnriqueAP6")
introducirDatoArchivo(nombreArchivo, "010203")
introducirDatoArchivo(nombreArchivo, "eap_6")
introducirDatoArchivo(nombreArchivo, "102030")
introducirDatoArchivo(nombreArchivo, "efjvdj")
introducirDatoArchivo(nombreArchivo, "odiewsnjd")
introducirDatoArchivo(nombreArchivo, "user")
introducirDatoArchivo(nombreArchivo, "password")

print(compruebaCredenciales(nombreArchivo,"eap_6","102030"))
print(compruebaCredenciales(nombreArchivo,"eap_6","password"))
print(compruebaCredenciales(nombreArchivo,"user","password"))


