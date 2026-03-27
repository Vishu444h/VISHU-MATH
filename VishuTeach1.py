from flask import Flask, render_template, request, send_file
from sympy import symbols, solve, diff, integrate, sympify
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
import pytesseract

# Custom folders
app = Flask(__name__, template_folder="vishu_math_templates", static_folder="vishu_math_static")
x = symbols('x')

@app.route("/", methods=["GET","POST"])
def index():
    answer = ""
    graph_url = None
    if request.method=="POST":
        q = request.form.get("question")
        try:
            if "=" in q:
                lhs,rhs = q.split("=")
                eq = sympify(lhs)-sympify(rhs)
                sol = solve(eq,x)
                answer = f"Solution: {sol}"
            elif q.startswith("diff"):
                f = q.replace("diff(","").replace(")","")
                answer = f"Derivative: {diff(sympify(f),x)}"
            elif q.startswith("int"):
                f = q.replace("int(","").replace(")","")
                answer = f"Integral: {integrate(sympify(f),x)}"
            elif q.startswith("plot"):
                f = q.replace("plot(","").replace(")","")
                func = sympify(f)
                xs = range(-10,11)
                ys = [func.subs(x,i) for i in xs]
                plt.figure()
                plt.plot(xs,ys, color='lime', linewidth=2)
                plt.title(f"Graph of {f}", color='lime')
                plt.savefig("vishu_math_static/graph.png")
                plt.close()
                graph_url = "vishu_math_static/graph.png"
                answer = "Graph Generated"
            else:
                res = sympify(q)
                answer = f"Answer: {res}"
        except Exception as e:
            answer = f"Error: {e}"
    return render_template("index.html", answer=answer, graph=graph_url)

@app.route("/pdf", methods=["POST"])
def download_pdf():
    text = request.form.get("answer")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.set_text_color(0,255,0)
    pdf.multi_cell(0,10, text)
    pdf_file = "solution.pdf"
    pdf.output(pdf_file)
    return send_file(pdf_file, as_attachment=True)

@app.route("/camera", methods=["POST"])
def camera():
    file = request.files['image']
    img = Image.open(file)
    text = pytesseract.image_to_string(img)
    return {"text": text.strip()}

if __name__=="__main__":
    app.run(debug=True)