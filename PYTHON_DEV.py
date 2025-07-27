def calculadora():
    n1 = float(input("QUAL É O PRIMEIRO NÚMERO? "))
    n2 = float(input("QUAL É O SEGUNDO NÚMERO? "))
    opera = input("QUAL É A OPERAÇÃO? (+, -, *, /) ")

    if opera == "+":
        resultado = n1 + n2
    elif opera == "-":
        resultado = n1 - n2
    elif opera == "*":
        resultado = n1 * n2
    elif opera == "/":
        if n2 != 0:
            resultado = n1 / n2
        else:
            return "Erro: Divisão por zero!"
    else:
        return "Operação inválida!"

    return calculadora 
 
print(calculadora())


from python_dev import calculadora  # importa a função

resultados = []

from python_dev import calculadora  # importa a função

resultados = []

#while True:
   # resposta = input("Quer fazer outro cálculo? (s/n): ").lower()
   # if resposta == "s":
    #    resultado = calculadora()
   #     resultados.append(resultado)
   # elif resposta == "n":
    #    break

# Exibe todos os resultados
#for i, res in enumerate(resultados, start=1):
    #print(f"{i}º cálculo: {res}")

