import io

def introducirDatoArchivo(nombreArchivo, lineaEscribir):
    
    archivoEscribir = open(nombreArchivo,"w")
    
    archivoEscribir.write(lineaEscribir[0]+"\n")
    archivoEscribir.write(lineaEscribir[1]+"\n")

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


