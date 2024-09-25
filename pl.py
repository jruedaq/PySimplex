import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# Función para resolver usando el método HiGHS
def resolver_simplex(coeficientes_objetivo, coeficientes_restricciones, valores_restricciones, coeficientes_igualdad=None, valores_igualdad=None, tipo_problema='max'):
    if tipo_problema == 'max':
        coeficientes_objetivo = -np.array(coeficientes_objetivo)  # Para maximización invertimos los coeficientes
    else:
        coeficientes_objetivo = np.array(coeficientes_objetivo)

    resultado = linprog(coeficientes_objetivo, A_ub=coeficientes_restricciones, b_ub=valores_restricciones, A_eq=coeficientes_igualdad, b_eq=valores_igualdad, method='highs')

    # Mostrar paso a paso
    print("----- Solución usando el Método Simplex -----")
    print("Coeficientes de la función objetivo: ", coeficientes_objetivo)
    print("Matriz de restricciones (≤): \n", coeficientes_restricciones)
    print("Valores de restricciones (≤): ", valores_restricciones)
    if coeficientes_igualdad is not None:
        print("Matriz de restricciones de igualdad: \n", coeficientes_igualdad)
        print("Valores de igualdad: ", valores_igualdad)
    print(f"Estado de la optimización: {'Maximización' if tipo_problema == 'max' else 'Minimización'}")
    print("Resultado:\n", resultado)
    print("---------------------------------------------\n")

    return resultado

# Función para resolver problemas 2D mediante método gráfico y sombrear la región factible
def generar_grafico(coeficientes_objetivo, coeficientes_restricciones, valores_restricciones, solucion_optima, tipos_restricciones):
    print("----- Solución usando el Método Gráfico -----")

    if len(coeficientes_objetivo) != 2:
        raise ValueError("El método gráfico solo se puede usar para dos variables.")

    # Valor máximo para los ejes basado en las restricciones
    maximo_x = max(valores_restricciones) / min([restriccion[0] for restriccion in coeficientes_restricciones if restriccion[0] > 0]) * 1.1
    maximo_y = max(valores_restricciones) / min([restriccion[1] for restriccion in coeficientes_restricciones if restriccion[1] > 0]) * 1.1

    # Definir el rango de valores para las gráficas
    valores_x = np.linspace(0, maximo_x, 400)

    # Variables para la región factible
    factible_y_superior = np.full_like(valores_x, maximo_y)
    factible_y_inferior = np.zeros_like(valores_x)

    # Graficar restricciones y actualizar el área factible
    for i in range(len(coeficientes_restricciones)):
        if coeficientes_restricciones[i][1] != 0:
            valores_y = (valores_restricciones[i] - coeficientes_restricciones[i][0] * valores_x) / coeficientes_restricciones[i][1]
            plt.plot(valores_x, valores_y, label=f'Restricción {i + 1}')

            if tipos_restricciones[i] == "<=":
                factible_y_superior = np.minimum(factible_y_superior, valores_y)
            elif tipos_restricciones[i] == ">=":
                factible_y_inferior = np.maximum(factible_y_inferior, valores_y)
        else:
            plt.axvline(x=valores_restricciones[i]/coeficientes_restricciones[i][0], label=f'Restricción {i + 1}')

    plt.xlim((0, maximo_x))
    plt.ylim((0, maximo_y))

    plt.xlabel('X1')
    plt.ylabel('X2')
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)

    # Sombrear la región factible
    plt.fill_between(valores_x, factible_y_inferior, factible_y_superior, where=(factible_y_superior >= factible_y_inferior), color='lightgreen', alpha=0.5, label='Región factible')

    # Marcar la solución óptima
    if solucion_optima is not None:
        plt.scatter(solucion_optima[0], solucion_optima[1], color='red', zorder=5, label='Solución óptima')
        plt.annotate(f'Solución óptima: ({solucion_optima[0]:.2f}, {solucion_optima[1]:.2f})',
                     xy=(solucion_optima[0], solucion_optima[1]), xytext=(solucion_optima[0] + 0.5, solucion_optima[1] - 0.5),
                     arrowprops=dict(facecolor='black', arrowstyle="->"), fontsize=10)

    plt.title('Método gráfico - Solución visual')
    plt.legend()
    plt.grid(True)
    plt.show()

# Función para calcular el valor de la función objetivo
def calcular_valor_objetivo(coeficientes_objetivo, valores_optimos_variables):
    valor_objetivo = np.dot(coeficientes_objetivo, valores_optimos_variables)  # Multiplicamos coeficientes por valores de las variables
    return valor_objetivo

# Función principal
def resolver_programa_lineal():
    print("Bienvenido al programa para resolver problemas de programación lineal.")

    tipo_problema = input("¿Desea maximizar o minimizar? (max/min): ").strip().lower()
    if tipo_problema not in ['max', 'min']:
        raise ValueError("Por favor, elija entre 'max' o 'min'.")

    numero_variables = int(input("Ingrese el número de variables: "))

    coeficientes_objetivo = []
    print(f"Ingrese los coeficientes de la función objetivo (de tamaño {numero_variables}):")
    for i in range(numero_variables):
        coeficiente = float(input(f"Coeficiente para x{i + 1}: "))
        coeficientes_objetivo.append(coeficiente)

    numero_restricciones = int(input("Ingrese el número de restricciones: "))

    coeficientes_restricciones = []
    valores_restricciones = []
    coeficientes_igualdad = []
    valores_igualdad = []
    tipos_restricciones = []

    print("Ingrese las restricciones")
    for i in range(numero_restricciones):
        coeficientes_restriccion = []
        for j in range(numero_variables):
            coeficiente = float(input(f"Coeficiente de x{j + 1} en la restricción {i + 1}: "))
            coeficientes_restriccion.append(coeficiente)

        operador = input("Ingrese el tipo de restricción (<=, >=, =): ").strip()
        valor_derecha = float(input(f"Valor en el lado derecho de la restricción {i + 1}: "))

        tipos_restricciones.append(operador)

        if operador == "<=":
            coeficientes_restricciones.append(coeficientes_restriccion)
            valores_restricciones.append(valor_derecha)
        elif operador == ">=":
            coeficientes_restricciones.append([-1 * x for x in coeficientes_restriccion])
            valores_restricciones.append(-valor_derecha)
        elif operador == "=":
            coeficientes_igualdad.append(coeficientes_restriccion)
            valores_igualdad.append(valor_derecha)
        else:
            raise ValueError("Operador no válido. Debe ser <=, >= o =.")

    coeficientes_restricciones = np.array(coeficientes_restricciones) if coeficientes_restricciones else None
    valores_restricciones = np.array(valores_restricciones) if valores_restricciones else None
    coeficientes_igualdad = np.array(coeficientes_igualdad) if coeficientes_igualdad else None
    valores_igualdad = np.array(valores_igualdad) if valores_igualdad else None

    # Resolver el problema de programación lineal usando el método Simplex
    resultado_simplex = resolver_simplex(coeficientes_objetivo, coeficientes_restricciones, valores_restricciones, coeficientes_igualdad, valores_igualdad, tipo_problema)

    # Mostrar valores de las variables óptimas
    print("----- Solución detallada -----")
    solucion_optima = []
    for i, valor_variable in enumerate(resultado_simplex.x, 1):
        solucion_optima.append(valor_variable)
        print(f"El valor de x{i} es: {valor_variable}")

    # Calcular y mostrar el valor óptimo de la función objetivo
    valor_optimo_objetivo = calcular_valor_objetivo(coeficientes_objetivo, resultado_simplex.x)
    print(f"El valor óptimo de la función objetivo, evaluando las variables obtenidas, es: {valor_optimo_objetivo}")

    # Método Gráfico solo para 2 variables y sombrear la región factible
    if numero_variables == 2:
        generar_grafico(coeficientes_objetivo, coeficientes_restricciones, valores_restricciones, solucion_optima, tipos_restricciones)
    else:
        print("El método gráfico solo está disponible para problemas de dos variables.")

if __name__ == "__main__":
    resolver_programa_lineal()
