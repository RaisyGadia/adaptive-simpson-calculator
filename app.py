from flask import Flask, render_template, request, jsonify
# In app.py, you should have:
from methods.adaptive_simpson import adaptive_simpson
import math

app = Flask(__name__)

def f(x, expression):
    """Safe evaluation of mathematical functions"""
    try:
        # Allow basic mathematical operations
        allowed_names = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
            'pi': math.pi, 'e': math.e
        }
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {**allowed_names, 'x': x})
        return float(result)
    except:
        return None

def adaptive_simpson(a, b, f_expr, tol=1e-6, max_depth=15):
    """
    Adaptive Simpson quadrature implementation
    """
    def simpson_rule(a, b):
        h = (b - a) / 2
        return (h / 3) * (f(a, f_expr) + 4*f(a + h, f_expr) + f(b, f_expr))
    
    def adaptive_simpson_recursive(a, b, tol, depth):
        m = (a + b) / 2
        S = simpson_rule(a, b)
        S_left = simpson_rule(a, m)
        S_right = simpson_rule(m, b)
        
        if depth >= max_depth:
            return S_left + S_right
        
        error = abs(S_left + S_right - S) / 15
        
        if error < tol:
            return S_left + S_right
        else:
            return (adaptive_simpson_recursive(a, m, tol/2, depth+1) + 
                    adaptive_simpson_recursive(m, b, tol/2, depth+1))
    
    return adaptive_simpson_recursive(a, b, tol, 0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adaptive-simpson', methods=['GET', 'POST'])
def adaptive_simpson_route():
    if request.method == 'POST':
        try:
            # Get form data
            a = float(request.form.get('a', 0))
            b = float(request.form.get('b', 1))
            function = request.form.get('function', 'x**2')
            tolerance = float(request.form.get('tolerance', 1e-6))
            
            # Calculate result
            result = adaptive_simpson(a, b, function, tolerance)
            
            # Calculate exact integral for comparison (if possible)
            exact = None
            if function == 'x**2':
                exact = (b**3 - a**3) / 3
            elif function == 'sin(x)':
                exact = -math.cos(b) + math.cos(a)
            elif function == 'cos(x)':
                exact = math.sin(b) - math.sin(a)
            
            return jsonify({
                'success': True,
                'result': result,
                'exact': exact,
                'error': abs(result - exact) if exact else None
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('adaptive_simpson.html')

@app.route('/examples')
def examples():
    return render_template('examples.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)