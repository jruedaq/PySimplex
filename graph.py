import matplotlib
matplotlib.use('Agg')  # Utilizar el backend 'Agg' para evitar abrir ventanas gráficas

import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from fractions import Fraction

# Función para resolver usando el método Simplex y mostrar las ecuaciones en formato LaTeX
def resolver_simplex_paso_a_paso(coeficientes_objetivo, restricciones, tipo_problema='max'):
    A_ub = []
    b_ub = []
    pasos = []  # Lista para mostrar las restricciones y la función objetivo

    # Convertir coeficientes a fracciones y construir restricciones
    for restriccion in restricciones:
        restriccion_frac = [Fraction(coef).limit_denominator() for coef in restriccion[:-2]]
        if restriccion[-1] == '<=':
            A_ub.append(restriccion_frac)  # Coeficientes de la restricción
            b_ub.append(Fraction(restriccion[-2]).limit_denominator())  # Lado derecho de la restricción
        elif restriccion[-1] == '>=':
            A_ub.append([-x for x in restriccion_frac])  # Invertir coeficientes para >=
            b_ub.append(Fraction(-restriccion[-2]).limit_denominator())  # Invertir el lado derecho

    # Definir la función objetivo con fracciones
    c_frac = [Fraction(coef).limit_denominator() for coef in coeficientes_objetivo]

    # Mostrar la configuración inicial con fracciones
    pasos.append("Función objetivo:")
    pasos.append(f"\\[ Z = {' + '.join([f'{coef}x_{{{i+1}}}' for i, coef in enumerate(c_frac)])} \\]")

    pasos.append("Restricciones:")
    for i, restriccion in enumerate(A_ub):
        restriccion_latex = ' + '.join([f'{coef}x_{{{j+1}}}' for j, coef in enumerate(restriccion)])
        pasos.append(f"\\[ {restriccion_latex} \\leq {b_ub[i]} \\]")

    # Resolver usando el método Simplex
    c = -np.array(coeficientes_objetivo) if tipo_problema == 'max' else np.array(coeficientes_objetivo)
    resultado = linprog(c, A_ub=np.array(A_ub, dtype=float), b_ub=np.array(b_ub, dtype=float), method='simplex')

    # Convertir los resultados a fracciones
    resultado_frac = [Fraction(x).limit_denominator() for x in resultado.x]
    valor_objetivo_frac = Fraction(resultado.fun).limit_denominator()

    return pasos, resultado_frac, valor_objetivo_frac

# Función para generar un gráfico que muestre la región factible y la solución óptima
def generar_grafico(coeficientes_objetivo, restricciones, img_path, solucion_optima):
    # Inicializar variables para el límite máximo de los ejes
    max_x = 0
    max_y = 0

    x = np.linspace(0, 100, 400)  # Ajustar el rango de x inicialmente a un valor grande
    factible_y_superior = np.full_like(x, 1000)  # Inicialmente un valor alto para la región superior
    factible_y_inferior = np.full_like(x, -1000)  # Inicialmente un valor bajo para la región inferior

    plt.figure()

    # Graficar restricciones
    for restriccion in restricciones:
        if restriccion[-1] == '<=':
            y = (restriccion[-2] - restriccion[0] * x) / restriccion[1]
            plt.plot(x, y, label=f'{restriccion[0]}x1 + {restriccion[1]}x2 <= {restriccion[-2]}')
            factible_y_superior = np.minimum(factible_y_superior, y)  # Actualizar región factible superior
        elif restriccion[-1] == '>=':
            y = (restriccion[-2] - restriccion[0] * x) / restriccion[1]
            plt.plot(x, y, label=f'{restriccion[0]}x1 + {restriccion[1]}x2 >= {restriccion[-2]}')
            factible_y_inferior = np.maximum(factible_y_inferior, y)  # Actualizar región factible inferior

        # Calcular el valor máximo de x y y en función de las restricciones
        max_x = max(max_x, restriccion[-2] / restriccion[0]) if restriccion[0] != 0 else max_x
        max_y = max(max_y, restriccion[-2] / restriccion[1]) if restriccion[1] != 0 else max_y

    # Sombrear la región factible (debe estar entre la superior e inferior)
    plt.fill_between(x, factible_y_inferior, factible_y_superior, where=(factible_y_superior >= factible_y_inferior), color='lightgreen', alpha=0.5)

    # Limitar los ejes de acuerdo a los valores calculados
    max_y_plot = max(factible_y_superior.max(), max_y)
    min_y_plot = max(factible_y_inferior.min(), 0)  # Aseguramos que el mínimo no sea menor a 0
    max_x_plot = max(max_x, 0)  # Aseguramos que x no sea menor a 0

    plt.xlim(0, max_x_plot * 1.2)  # Añadir un margen del 20% en el eje x
    plt.ylim(min_y_plot * 1.2, max_y_plot * 1.2)  # Añadir un margen del 20% en el eje y

    # Dibujar la solución óptima
    if solucion_optima is not None:
        plt.scatter(solucion_optima[0], solucion_optima[1], color='red', zorder=5)
        plt.text(solucion_optima[0], solucion_optima[1], f'Solución óptima ({solucion_optima[0]:.2f}, {solucion_optima[1]:.2f})', fontsize=10, verticalalignment='bottom', color='red')

    # Etiquetas y leyenda
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.legend()
    plt.grid(True)

    # Guardar el gráfico
    plt.savefig(img_path)
    plt.close()

# Función para calcular el valor de la función objetivo
def calcular_valor_objetivo(coeficientes_objetivo, valores_optimos):
    return np.dot(coeficientes_objetivo, valores_optimos)
