import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

data = None
model = None
X = None
y = None

transactions_checked = 0
frauds_detected = 0
is_monitoring = False
monitor_id = None

def load_data():
    global data
    try:
        data = pd.read_csv("creditcard_augmented.csv")
        messagebox.showinfo("Success", "Dataset Loaded Successfully!")
    except FileNotFoundError:
        data = pd.read_csv("creditcard.csv")
        messagebox.showinfo("Success", "Dataset Loaded Successfully! (Fallback to original)")


def train_model():
    global model, X, y

    if data is None:
        messagebox.showerror("Error", "Load dataset first!")
        return

    X = data.drop("Class", axis=1)
    y = data["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    messagebox.showinfo("Success", "Model trained successfully!")

def show_graph():

    fraud_count = data["Class"].value_counts()

    labels = ["Normal", "Fraud"]

    plt.figure(figsize=(6,6))
    plt.pie(fraud_count, labels=labels, autopct='%0.2f%%')
    plt.title("Fraud vs Normal Transactions")
    plt.show()

def update_dashboard():

    fraud_rate = 0

    if transactions_checked > 0:
        fraud_rate = (frauds_detected / transactions_checked) * 100

    total_label.config(text=str(transactions_checked))
    fraud_label.config(text=str(frauds_detected))
    rate_label.config(text=f"{round(fraud_rate,2)}%")

def check_transaction():

    global transactions_checked, frauds_detected

    if model is None:
        messagebox.showerror("Error", "Train model first!")
        return

    try:
        amount = float(amount_entry.get())
        time = float(time_entry.get())

        sample = X.iloc[0].values
        sample[0] = time
        sample[-1] = amount

        input_df = pd.DataFrame([sample], columns=X.columns)

        probability = model.predict_proba(input_df)[0][1]
        risk = round(probability * 100, 2)

        transactions_checked += 1

        if risk > 40:
            result = "Fraud"
            result_label.config(text="Fraudulent Transaction", fg="red")
            frauds_detected += 1

        elif risk > 10:
            result = "Suspicious"
            result_label.config(text="Suspicious Transaction", fg="orange")

        else:
            result = "Legitimate"
            result_label.config(text="Legitimate Transaction", fg="green")

        risk_label.config(text=f"Fraud Risk Score: {risk}%")

        table.insert("", 0, values=(time, amount, risk, result))

        update_dashboard()

    except:
        messagebox.showerror("Error", "Enter valid values")


def process_live_transaction():
    global transactions_checked, frauds_detected, is_monitoring, monitor_id

    if not is_monitoring:
        return

    if model is None:
        messagebox.showerror("Error", "Train model first!")
        stop_monitoring()
        return

    sample_row = X.sample(1)

    probability = model.predict_proba(sample_row)[0][1]
    risk = round(probability * 100, 2)

    time = sample_row.iloc[0]["Time"]
    amount = sample_row.iloc[0]["Amount"]

    transactions_checked += 1

    if risk > 40:
        result = "Fraud"
        frauds_detected += 1
    elif risk > 10:
        result = "Suspicious"
    else:
        result = "Legitimate"

    table.insert("", 0, values=(time, amount, risk, result))
    update_dashboard()

    monitor_id = root.after(2000, process_live_transaction)

def start_monitoring():
    global is_monitoring
    if model is None:
        messagebox.showerror("Error", "Train model first!")
        return
    if not is_monitoring:
        is_monitoring = True
        process_live_transaction()

def stop_monitoring():
    global is_monitoring, monitor_id
    is_monitoring = False
    if monitor_id:
        root.after_cancel(monitor_id)
        monitor_id = None


root = tk.Tk()
root.title("🛡️ Fraud Transaction Detection System")
root.geometry("900x650")
root.configure(bg="#F0F4F8")  


style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#2C3E50", font=("Segoe UI", 10), rowheight=25)
style.configure("Treeview.Heading", background="#BAE1FF", foreground="#2C3E50", font=("Segoe UI", 11, "bold"))
style.map("Treeview", background=[("selected", "#FFDFBA")], foreground=[("selected", "#2C3E50")])


title = tk.Label(
    root,
    text="Fraud Transaction Detection System",
    font=("Segoe UI", 24, "bold"),
    bg="#F0F4F8",
    fg="#2C3E50"
)
title.pack(pady=15)


main_frame = tk.Frame(root, bg="#F0F4F8")
main_frame.pack(fill="both", expand=True, padx=20, pady=5)


left_panel = tk.Frame(main_frame, bg="#F0F4F8", width=300)
left_panel.pack(side="left", fill="y", padx=10)


right_panel = tk.Frame(main_frame, bg="#F0F4F8")
right_panel.pack(side="right", fill="both", expand=True, padx=10)

btn_frame = tk.LabelFrame(left_panel, text=" Actions ", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#2C3E50", padx=15, pady=15, relief="flat")
btn_frame.pack(fill="x", pady=10, ipadx=5, ipady=5)

def create_btn(parent, text, color, command):
    return tk.Button(parent, text=text, bg=color, fg="#2C3E50", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", command=command, pady=5)

load_btn = create_btn(btn_frame, "Load Dataset", "#FFB3BA", load_data)
load_btn.pack(fill="x", pady=5)

train_btn = create_btn(btn_frame, "Train Model", "#BAFFC9", train_model)
train_btn.pack(fill="x", pady=5)

graph_btn = create_btn(btn_frame, "Show Fraud Graph", "#BAE1FF", show_graph)
graph_btn.pack(fill="x", pady=5)

start_btn = create_btn(btn_frame, "Start Live Monitoring", "#FFFFBA", start_monitoring)
start_btn.pack(fill="x", pady=5)

stop_btn = create_btn(btn_frame, "Stop Live Monitoring", "#FFC8C8", stop_monitoring)
stop_btn.pack(fill="x", pady=5)


input_frame = tk.LabelFrame(left_panel, text=" Manual Check ", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#2C3E50", padx=15, pady=15, relief="flat")
input_frame.pack(fill="x", pady=10, ipadx=5, ipady=5)

tk.Label(input_frame, text="Transaction Time (e.g. 0.0):", bg="#FFFFFF", fg="#2C3E50", font=("Segoe UI", 10)).pack(anchor="w")
time_entry = tk.Entry(input_frame, font=("Segoe UI", 11), bg="#F8F9F9", relief="solid", bd=1)
time_entry.pack(fill="x", pady=3)

tk.Label(input_frame, text="Transaction Amount (e.g. 150):", bg="#FFFFFF", fg="#2C3E50", font=("Segoe UI", 10)).pack(anchor="w", pady=(5,0))
amount_entry = tk.Entry(input_frame, font=("Segoe UI", 11), bg="#F8F9F9", relief="solid", bd=1)
amount_entry.pack(fill="x", pady=3)

check_btn = create_btn(input_frame, "Check Transaction", "#D5AAFF", check_transaction) # Pastel purple
check_btn.pack(fill="x", pady=10)

risk_label = tk.Label(input_frame, text="", font=("Segoe UI", 11, "bold"), bg="#FFFFFF")
risk_label.pack()

result_label = tk.Label(input_frame, text="", font=("Segoe UI", 13, "bold"), bg="#FFFFFF")
result_label.pack(pady=5)



dashboard_frame = tk.Frame(right_panel, bg="#F0F4F8")
dashboard_frame.pack(fill="x", pady=(0, 10))

def create_stat_card(parent, title, value, color):
    card = tk.Frame(parent, bg=color, padx=15, pady=10, relief="flat")
    card.pack(side="left", expand=True, fill="both", padx=5)
    title_lbl = tk.Label(card, text=title, font=("Segoe UI", 10), bg=color, fg="#2C3E50")
    title_lbl.pack()
    val_lbl = tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg=color, fg="#2C3E50")
    val_lbl.pack()
    return val_lbl

total_label = create_stat_card(dashboard_frame, "Transactions Checked", "0", "#E8F8F5")
fraud_label = create_stat_card(dashboard_frame, "Frauds Detected", "0", "#FDEDEC")
rate_label = create_stat_card(dashboard_frame, "Fraud Rate", "0%", "#FEF9E7")

table_frame = tk.Frame(right_panel, bg="#FFFFFF", bd=0, relief="flat")
table_frame.pack(fill="both", expand=True, pady=5)

columns = ("Time", "Amount", "Risk %", "Result")
table = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    if col == "Result":
        table.column(col, anchor="center", width=150)
    else:
        table.column(col, anchor="center", width=100)


scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
table.pack(side="left", fill="both", expand=True)


root.mainloop()
