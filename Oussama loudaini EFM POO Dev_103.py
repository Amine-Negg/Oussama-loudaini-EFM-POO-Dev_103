import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ==========================================
# PARTIE 1 & 2 : Définition des Classes (Backend)
# ==========================================

class Patient:
    def __init__(self, cin, nom, prenom, age, date_entree="", date_sortie=""):
        self.cin = cin
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.date_entree = date_entree
        self.date_sortie = date_sortie

    def afficher(self):
        return f"Patient: {self.nom} {self.prenom}, CIN: {self.cin}, Age: {self.age}"

class Medecin:
    def __init__(self, nom, specialite):
        self.nom = nom
        self.specialite = specialite

    def afficher(self):
        return f"Médecin: {self.nom}, Spécialité: {self.specialite}"

class Hospitalisation:
    def __init__(self, id_patient, id_medecin, date_debut="", date_fin=""):
        self.id_patient = id_patient
        self.id_medecin = id_medecin
        self.date_debut = date_debut
        self.date_fin = date_fin


# ==========================================
# PARTIE 4 : Interface Graphique et Base de données (Frontend)
# ==========================================

class AppHopital(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Logiciel Hospitalier POO")
        self.geometry("900x600")
        
        # Initialisation de la base de données
        self.init_db()
        
        # Création de l'interface
        self.create_widgets()
        
        # Affichage initial de la liste
        self.display_patients()

    def init_db(self):
        """Initialise la connexion SQLite et crée les tables si elles n'existent pas"""
        self.conn = sqlite3.connect('hopital.db')
        self.cur = self.conn.cursor()
        
        # Création table Patient
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cin TEXT UNIQUE,
                nom TEXT,
                prenom TEXT,
                age INTEGER,
                date_entree TEXT,
                date_sortie TEXT
            )
        ''')
        
        # Création table Médecin
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS medecins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                specialite TEXT
            )
        ''')
        
        # Création table Hospitalisation
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS hospitalisations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_patient INTEGER,
                id_medecin INTEGER,
                date_debut TEXT,
                date_fin TEXT,
                FOREIGN KEY (id_patient) REFERENCES patients(id),
                FOREIGN KEY (id_medecin) REFERENCES medecins(id)
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        """Construction de l'interface utilisateur avec Tkinter"""
        
        # --- Frame pour les entrées (Formulaire) ---
        form_frame = tk.LabelFrame(self, text="Formulaire Patient", padx=10, pady=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        # Entrées (CIN, Nom, Prénom, Age, Dates)
        tk.Label(form_frame, text="CIN:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_cin = tk.Entry(form_frame, width=20)
        self.entry_cin.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Nom:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_nom = tk.Entry(form_frame, width=20)
        self.entry_nom.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Prénom:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_prenom = tk.Entry(form_frame, width=20)
        self.entry_prenom.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Âge:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_age = tk.Entry(form_frame, width=20)
        self.entry_age.grid(row=1, column=3, padx=5, pady=5)
        
        # (Ajout facultatif des dates pour correspondre aux attributs, mais si on veut coller à la capture d'écran, on peut les omettre ici. Je les inclus pour respecter le texte de l'examen)
        tk.Label(form_frame, text="Date Entrée (JJ/MM/AAAA):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_date_entree = tk.Entry(form_frame, width=20)
        self.entry_date_entree.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Date Sortie (JJ/MM/AAAA):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_date_sortie = tk.Entry(form_frame, width=20)
        self.entry_date_sortie.grid(row=2, column=3, padx=5, pady=5)

        # --- Frame pour les boutons d'action ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Ajouter", command=self.add_patient, bg="#d4edda", fg="black", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Afficher (Liste)", command=self.display_patients, bg="#cce5ff", fg="black", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Modifier", command=self.update_patient, bg="#ffeeba", fg="black", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_patient, bg="#f8d7da", fg="black", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Quitter", command=self.destroy, bg="#f5c6cb", fg="black", width=15).pack(side="left", padx=5)

        # --- Frame pour la liste (Treeview) ---
        list_frame = tk.LabelFrame(self, text="Liste des Patients", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Définition des colonnes
        columns = ("ID", "CIN", "Nom", "Prénom", "Âge", "Date Entrée", "Date Sortie")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)
        
        # Bind event : cliquer sur une ligne pour remplir le formulaire
        self.tree.bind("<ButtonRelease-1>", self.on_item_select)

    def add_patient(self):
        """Fonctionnalité 1 : Ajouter un patient"""
        cin = self.entry_cin.get()
        nom = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        age = self.entry_age.get()
        date_entree = self.entry_date_entree.get()
        date_sortie = self.entry_date_sortie.get()

        if not cin or not nom or not prenom or not age:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            self.cur.execute("INSERT INTO patients (cin, nom, prenom, age, date_entree, date_sortie) VALUES (?, ?, ?, ?, ?, ?)", 
                             (cin, nom, prenom, age, date_entree, date_sortie))
            self.conn.commit()
            messagebox.showinfo("Succès", "Patient ajouté avec succès.")
            self.display_patients()  # Rafraîchir la liste
            self.clear_entries()     # Vider le formulaire
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Un patient avec ce CIN existe déjà.")

    def display_patients(self):
        """Fonctionnalité 2 : Afficher la liste des patients"""
        # Efface l'affichage actuel
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.cur.execute("SELECT * FROM patients")
        rows = self.cur.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_item_select(self, event):
        """Remplit le formulaire quand on clique sur une ligne de la liste"""
        item = self.tree.selection()
        if item:
            values = self.tree.item(item[0], 'values')
            self.entry_cin.delete(0, tk.END)
            self.entry_cin.insert(0, values[1]) # CIN
            self.entry_nom.delete(0, tk.END)
            self.entry_nom.insert(0, values[2]) # Nom
            self.entry_prenom.delete(0, tk.END)
            self.entry_prenom.insert(0, values[3]) # Prénom
            self.entry_age.delete(0, tk.END)
            self.entry_age.insert(0, values[4]) # Âge
            self.entry_date_entree.delete(0, tk.END)
            self.entry_date_entree.insert(0, values[5]) # Date Entrée
            self.entry_date_sortie.delete(0, tk.END)
            self.entry_date_sortie.insert(0, values[6]) # Date Sortie

    def update_patient(self):
        """Fonctionnalité : Modifier un patient existant (basé sur le CIN)"""
        cin = self.entry_cin.get()
        if not cin:
            messagebox.showerror("Erreur", "Veuillez sélectionner un patient (via son CIN) à modifier.")
            return
        
        nom = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        age = self.entry_age.get()
        date_entree = self.entry_date_entree.get()
        date_sortie = self.entry_date_sortie.get()

        self.cur.execute("""
            UPDATE patients 
            SET nom=?, prenom=?, age=?, date_entree=?, date_sortie=?
            WHERE cin=?
        """, (nom, prenom, age, date_entree, date_sortie, cin))
        
        self.conn.commit()
        messagebox.showinfo("Succès", "Patient modifié avec succès.")
        self.display_patients()
        self.clear_entries()

    def delete_patient(self):
        """Fonctionnalité 5 : Supprimer un patient"""
        item = self.tree.selection()
        if not item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un patient à supprimer.")
            return
        
        # Récupérer l'ID du patient (première colonne de la ligne sélectionnée)
        values = self.tree.item(item[0], 'values')
        patient_id = values[0]
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce patient ?"):
            self.cur.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            self.conn.commit()
            
            # Supprimer aussi les hospitalisations liées à ce patient (si on veut maintenir l'intégrité)
            self.cur.execute("DELETE FROM hospitalisations WHERE id_patient=?", (patient_id,))
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Patient supprimé avec succès.")
            self.display_patients()
            self.clear_entries()

    def clear_entries(self):
        """Vider les champs du formulaire"""
        self.entry_cin.delete(0, tk.END)
        self.entry_nom.delete(0, tk.END)
        self.entry_prenom.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.entry_date_entree.delete(0, tk.END)
        self.entry_date_sortie.delete(0, tk.END)


# ==========================================
# Lancement de l'application
# ==========================================
if __name__ == "__main__":
    app = AppHopital()
    app.mainloop()