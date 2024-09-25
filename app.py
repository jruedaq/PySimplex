from flask import Flask, render_template, request
from graph import generar_grafico, resolver_simplex_paso_a_paso, calcular_valor_objetivo
from fractions import Fraction

app = Flask(__name__)

# Función para convertir fracciones a flotantes
def convertir_a_float(valor):
    try:
        # Intentar convertir a fracción primero
        return float(Fraction(valor))
    except ValueError:
        return None  # En caso de error, devuelve None para manejar después

# Ruta principal: Mostrar el formulario para número de variables, restricciones y tipo de problema
@app.route('/')
def index():
    return render_template('inicio.html')

# Ruta para mostrar el formulario basado en el número de variables y restricciones
@app.route('/formulario', methods=['POST'])
def formulario():
    # Obtener los valores ingresados
    num_variables = int(request.form.get('num_variables'))
    num_restricciones = int(request.form.get('num_restricciones'))
    tipo_problema = request.form.get('tipo_problema')

    return render_template('formulario.html', num_variables=num_variables, num_restricciones=num_restricciones, tipo_problema=tipo_problema)

# Ruta para resolver el problema de programación lineal
@app.route('/resolver', methods=['POST'])
def resolver():
    # Obtener datos del formulario
    num_variables = int(request.form.get('num_variables'))
    num_restricciones = int(request.form.get('num_restricciones'))
    tipo_problema = request.form.get('tipo_problema')

    # Obtener coeficientes de la función objetivo y convertir a flotantes o fracciones
    coeficientes = request.form.get('coeficiente').split(',')
    coef_objetivo = []
    for coef in coeficientes:
        valor = convertir_a_float(coef)
        if valor is None:
            return "Error: Por favor, ingresa números válidos o fracciones en los coeficientes.", 400
        coef_objetivo.append(valor)

    # Procesar restricciones
    restricciones = []
    for i in range(num_restricciones):
        coeficientes_restriccion = request.form.get(f'restriccion_{i + 1}').split(',')
        coef_restriccion = []
        for coef in coeficientes_restriccion:
            valor = convertir_a_float(coef)
            if valor is None:
                return f"Error: Por favor, ingresa números válidos o fracciones en la restricción {i + 1}.", 400
            coef_restriccion.append(valor)

        # Obtener el operador de la restricción (<= o >=)
        operador = request.form.get(f'operador_{i + 1}')

        if len(coef_restriccion) != num_variables + 1:
            return f"Error: El número de coeficientes en la restricción {i + 1} no coincide con el número de variables.", 400

        restricciones.append(coef_restriccion + [operador])

    # Llamar a la función resolver_simplex_paso_a_paso
    pasos, resultado_simplex, valor_objetivo = resolver_simplex_paso_a_paso(coef_objetivo, restricciones, tipo_problema)

    # Generar gráfico si hay dos variables
    img_path = None
    if num_variables == 2:
        img_path = 'static/images/grafico.png'
        generar_grafico(coef_objetivo, restricciones, img_path, resultado_simplex)

    # Renderizar la página con los resultados
    return render_template('resultado.html', pasos=pasos, resultado=resultado_simplex, valor_objetivo=valor_objetivo, img_path=img_path)

if __name__ == '__main__':
    app.run(debug=True)
