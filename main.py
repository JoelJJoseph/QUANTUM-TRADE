from qiskit import Aer
from qiskit.aqua import QuantumInstance
from qiskit.finance.applications.ising import portfolio
from qiskit.circuit.library import TwoLocal
from qiskit.aqua.algorithms import VQE, QAOA
from qiskit.optimization.applications.ising.common import sample_most_likely
from qiskit.finance.data_providers import WikipediaDataProvider
from qiskit.aqua.components.optimizers import COBYLA
import warnings
from matplotlib.cbook import MatplotlibDeprecationWarning
import datetime
import numpy as np
from tkinter import *
from tkinter import messagebox
import webbrowser

warnings.filterwarnings('ignore', category=MatplotlibDeprecationWarning)
GOLD = "#FFD700"





def display(out):
    messagebox.showinfo("Best Stock Option", f"The best stocks to buy are:\n{out}")



def re_d():
    webbrowser.open("https://markets.businessinsider.com/stocks")
    return



def out():
    stocks = list(symbol_entry.get().split(","))
    print(stocks)
    if len(stocks) > 0:
        is_ok = messagebox.askokcancel(stocks,
                                       f"The stocks you entered are:\n Stocks:{stocks}\n Do you want to proceed?")
        if is_ok:
            try:

                token = "****55555****"
                num_assets = len(stocks)
                wiki = WikipediaDataProvider(token=token,
                                             tickers=stocks,
                                             start=datetime.datetime(2017, 8, 15),
                                             end=datetime.datetime(2021, 3, 5))
                wiki.run()

                mu = wiki.get_period_return_mean_vector()
                sigma = wiki.get_period_return_covariance_matrix()
                q = 0.5  # set risk factor
                budget = 2  # set budget
                penalty = num_assets  # set parameter to scale the budget penalty term

                qubitOp, offset = portfolio.get_operator(mu, sigma, q, budget, penalty)

                # Prep for solvers
                seed = 50

                # Set up the classical optimiser
                cobyla = COBYLA()
                cobyla.set_options(maxiter=500)

                # Set up the quantum instance backend
                backend = Aer.get_backend('statevector_simulator')
                quantum_instance = QuantumInstance(backend=backend, shots=8000, seed_simulator=seed,
                                                   seed_transpiler=seed)

                qaoa_counts = []
                qaoa_values = []

                def store(counts, para, mean, std):
                    qaoa_counts.append(counts)
                    qaoa_values.append(mean)

                qaoa = QAOA(qubitOp, cobyla, 1, callback=store)
                qaoa.random_seed = seed

                qaoa_result = qaoa.run(quantum_instance)

                def index_to_selection(i, num_assets):
                    s = "{0:b}".format(i).rjust(num_assets)
                    x = np.array([1 if s[i] == '1' else 0 for i in reversed(range(num_assets))])
                    return x

                li = []

                def print_result(result):
                    selection = sample_most_likely(result.eigenstate)
                    value = portfolio.portfolio_value(selection, mu, sigma, q, budget, penalty)
                    print(list(selection))
                    answer = selection.tolist()
                    s = ""
                    for i in range(num_assets):
                        if (answer[i] == 1):
                            s = s + f"{stocks[i],}"
                    display(s)

                backend = Aer.get_backend('statevector_simulator')
                seed = 50

                cobyla = COBYLA()
                cobyla.set_options(maxiter=500)
                ry = TwoLocal(qubitOp.num_qubits, 'ry', 'cz', reps=3, entanglement='full')
                vqe = VQE(qubitOp, ry, cobyla)
                vqe.random_seed = seed

                quantum_instance = QuantumInstance(backend=backend, seed_simulator=seed, seed_transpiler=seed)

                result = vqe.run(quantum_instance)

                print_result(result)

                pass
            except FileNotFoundError:
                pass
            else:
                pass
            finally:
                symbol_entry.delete(0, END)
    else:
        messagebox.showerror("Error", "You cannot leave any of the fields empty!")

    return


# generate UI
window = Tk()
window.title("Quantum Trade")
window.geometry("500x500")
window.config(padx=100, pady=50, bg="white")

bg = PhotoImage(file="bg1.png")
canvas1 = Canvas(width=500, height=500, highlightthickness=0)
canvas1.place(x=-100, y=0)
canvas1.create_image(0, 0, image=bg, anchor="nw")





symbol_label = Label(text="STOCK OR BITCOIN SYMBOLS:", bg=GOLD)
symbol_label.grid(row=2, column=0)

symbol_entry = Entry(width=40)
symbol_entry.grid(row=5, column=0)
symbol_entry.insert(0, "SYMBOLS")
symbol_entry.focus()

re_d_btn = Button(text="Get Symbols", width=30, highlightthickness=0, bg=GOLD, command=re_d)
re_d_btn.grid(row=8, column=0)

out_btn = Button(text="Get Best Stock Option", width=50, highlightthickness=0, bg=GOLD, command=out)
out_btn.grid(row=7, column=0, columnspan=2)



window.mainloop()
