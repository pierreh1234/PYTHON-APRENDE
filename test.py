from python_dev import calculadora  # importa a função

resultados = []

while True:
    resposta = input("Quer fazer outro cálculo? (s/n): ").lower()
    if resposta == "s":
        resultado = calculadora()
        resultados.append(resultado)
    elif resposta == "n":
        break

# Exibe todos os resultados
for i, res in enumerate(resultados, start=1):
    print(f"{i}º cálculo: {res}")
