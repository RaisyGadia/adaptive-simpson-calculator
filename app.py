from flask import Flask, render_template, request, jsonify
import math
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

def safe_math_function(x, expression):
    """Safe evaluation of mathematical functions"""
    try:
        # Allowed mathematical functions
        allowed_names = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'sqrt': math.sqrt,
            'abs': abs,
            'pi': math.pi,
            'e': math.e
        }
        
        # Check for dangerous patterns
        dangerous = ['__', 'import', 'exec', 'eval', 'compile', 'open', 'file']
        for pattern in dangerous:
            if pattern in expression.lower():
                return None
        
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, {**allowed_names, 'x': x})
        return float(result)
    except Exception:
        return None

def adaptive_simpson_rule(a, b, f_expr, tol=1e-6, max_depth=15):
    """Adaptive Simpson quadrature implementation"""
    
    def simpson(f, a, b):
        h = (b - a) / 2
        return (h / 3) * (f(a) + 4*f(a + h) + f(b))
    
    def recursive_simpson(a, b, tol, depth):
        # Create function wrapper
        def f_eval(x):
            return safe_math_function(x, f_expr) or 0
        
        m = (a + b) / 2
        S = simpson(f_eval, a, b)
        S_left = simpson(f_eval, a, m)
        S_right = simpson(f_eval, m, b)
        
        if depth >= max_depth:
            return S_left + S_right
        
        error = abs(S_left + S_right - S) / 15
        
        if error < tol:
            return S_left + S_right
        else:
            return (recursive_simpson(a, m, tol/2, depth+1) + 
                    recursive_simpson(m, b, tol/2, depth+1))
    
    try:
        return recursive_simpson(a, b, tol, 0)
    except:
        return None

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
            
            # Validate inputs
            if a >= b:
                return jsonify({'success': False, 'error': 'Lower limit must be less than upper limit'}), 400
            
            if tolerance <= 0 or tolerance > 1:
                return jsonify({'success': False, 'error': 'Tolerance must be between 0 and 1'}), 400
            
            # Calculate result
            result = adaptive_simpson_rule(a, b, function, tolerance)
            
            if result is None:
                return jsonify({'success': False, 'error': 'Calculation failed. Check your function.'}), 400
            
            # Calculate exact integral for common functions
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

# This is required for Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True)