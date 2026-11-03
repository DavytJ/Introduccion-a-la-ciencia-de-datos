objeto1 <- c(1,2,3)

objeto_caracter <- c("1","2","3")

#objeto2 <- objeto1*3

objeto_caracter <- as.numeric(c("1","2","3")) # funcion para transformar vectores

# crear categoría

objeto_caracter <- c("A","B","C")

objeto_caracter <- as.factor(objeto_caracter)

class(objeto_caracter)


df <- cbind(objeto1, objeto2, objeto_caracter)

df[1,2]
class(df)

df2 <- as.data.frame(df)
class(df2)

objeto3 <- c("Franco", "Valentina", "Florencia")

df2 <- cbind(df2, objeto3)

objeto4 <- c("silla", "mesa", "")

objeto5 <- c("silla", "mesa", NA)
