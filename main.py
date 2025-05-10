import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import random
import string
import json
import os

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("800x600")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.passwords_file = "passwords.json"
        self.passwords = self.load_passwords()
        
        self.notebook = ctk.CTkTabview(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.notebook.add("Password Generator")
        self.notebook.add("Password Manager")
        
        self.create_generator_tab()
        self.create_manager_tab()

    def create_generator_tab(self):
        tab = self.notebook.tab("Password Generator")
        
        ctk.CTkLabel(tab, text="Password Strength:").pack(pady=5)
        self.strength_var = ctk.StringVar(value="Medium (18 chars)")
        strengths = ["Low (12 chars)", "Medium (18 chars)", "High (24 chars)"]
        self.strength_combo = ctk.CTkComboBox(
            tab, 
            values=strengths, 
            variable=self.strength_var, 
            state="readonly"
        )
        self.strength_combo.pack(pady=5)
        
        self.password_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            tab, 
            textvariable=self.password_var, 
            state="readonly", 
            font=('Courier', 12),
            width=400
        )
        entry.pack(pady=10, fill='x', padx=10)
        
        ctk.CTkButton(
            tab, 
            text="Generate Password", 
            command=self.generate_password
        ).pack(pady=5)
        
        frame = ctk.CTkFrame(tab)
        frame.pack(pady=10, fill='x', padx=10)
        
        ctk.CTkLabel(frame, text="Service:").grid(row=0, column=0, sticky='w', padx=5)
        self.service_entry = ctk.CTkEntry(frame, width=300)
        self.service_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        ctk.CTkLabel(frame, text="Username:").grid(row=1, column=0, sticky='w', padx=5)
        self.username_entry = ctk.CTkEntry(frame, width=300)
        self.username_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        ctk.CTkButton(
            frame, 
            text="Save", 
            command=self.save_to_manager
        ).grid(row=2, column=0, columnspan=2, pady=10)

    def create_manager_tab(self):
        tab = self.notebook.tab("Password Manager")
        
        ctk.CTkLabel(tab, text="Search:").pack(pady=5)
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(tab, textvariable=self.search_var, width=400)
        search_entry.pack(fill='x', padx=10, pady=5)
        search_entry.bind('<KeyRelease>', self.filter_passwords)
        
        self.listbox = ctk.CTkTextbox(tab, height=300)
        self.listbox.pack(fill='both', expand=True, padx=10, pady=5)
        self.listbox.bind('<Double-Button-1>', self.show_password_details)
        self.listbox.configure(state='disabled')
        
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="View Details", 
            command=self.show_password_details
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Delete", 
            command=self.delete_password
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Export All", 
            command=self.export_passwords
        ).pack(side='right', padx=5)
        
        self.update_password_list()

    def generate_password(self):
        """Generate a password based on selected strength"""
        strength = self.strength_combo.get()
        length = 12 if "Low" in strength else 18 if "Medium" in strength else 24
        
        chars = string.ascii_letters
        special_chars = string.punctuation
        nums = string.digits
        
        each = length // 3
        remainder = length % 3
        
        password_parts = [
            random.choices(chars, k=each + (1 if remainder > 0 else 0)),
            random.choices(special_chars, k=each + (1 if remainder > 1 else 0)),
            random.choices(nums, k=each)
        ]
        
        password_chars = [char for part in password_parts for char in part]
        random.shuffle(password_chars)
        
        password = ''.join(password_chars)
        self.password_var.set(password)

    def save_to_manager(self):
        """Save the generated password to the manager"""
        password = self.password_var.get()
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not password:
            messagebox.showwarning("Warning", "Please generate a password first!")
            return
            
        if not service:
            messagebox.showwarning("Warning", "Please enter a service name!")
            return
            
        for pwd in self.passwords:
            if pwd['service'].lower() == service.lower():
                reply = messagebox.askyesno(
                    'Confirm', 
                    f"A password already exists for {service}. Overwrite?"
                )
                if not reply:
                    return
                self.passwords = [p for p in self.passwords if p['service'].lower() != service.lower()]
                break
        
        self.passwords.append({
            'service': service,
            'username': username,
            'password': password
        })
        
        self.save_passwords()
        self.update_password_list()
        
        self.service_entry.delete(0, 'end')
        self.username_entry.delete(0, 'end')
        
        messagebox.showinfo("Success", "Password saved successfully!")

    def load_passwords(self):
        """Load passwords from JSON file"""
        if os.path.exists(self.passwords_file):
            try:
                with open(self.passwords_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_passwords(self):
        """Save passwords to JSON file"""
        with open(self.passwords_file, 'w') as f:
            json.dump(self.passwords, f, indent=4)

    def update_password_list(self):
        """Update the password list widget"""
        self.listbox.configure(state='normal')
        self.listbox.delete('1.0', 'end')
        for pwd in sorted(self.passwords, key=lambda x: x['service'].lower()):
            self.listbox.insert('end', f"{pwd['service']} - {pwd['username']}\n")
        self.listbox.configure(state='disabled')

    def filter_passwords(self, event=None):
        """Filter passwords based on search text"""
        search_text = self.search_var.get().lower()
        self.listbox.configure(state='normal')
        self.listbox.delete('1.0', 'end')
        
        for pwd in self.passwords:
            if (search_text in pwd['service'].lower() or 
                search_text in pwd['username'].lower()):
                self.listbox.insert('end', f"{pwd['service']} - {pwd['username']}\n")
        self.listbox.configure(state='disabled')

    def show_password_details(self, event=None):
        """Show details of the selected password"""
        try:
            selected_line = self.listbox.get('1.0', 'end').split('\n')[int(self.listbox.index('current').split('.')[0])-1]
            if not selected_line.strip():
                return
            
            service = selected_line.split(" - ")[0]
            
            for pwd in self.passwords:
                if pwd['service'] == service:
                    master_pwd = simpledialog.askstring(
                        "Authentication", 
                        "Enter your master password to view:",
                        show='*'
                    )
                    
                    if master_pwd == "admin123":
                        details = (
                            f"Service: {pwd['service']}\n"
                            f"Username: {pwd['username']}\n"
                            f"Password: {pwd['password']}"
                        )
                        messagebox.showinfo("Password Details", details)
                    else:
                        messagebox.showerror("Error", "Incorrect master password!")
                    break
        except IndexError:
            messagebox.showwarning("Warning", "Please select a password first!")

    def delete_password(self):
        """Delete the selected password"""
        try:
            selected_line = self.listbox.get('1.0', 'end').split('\n')[int(self.listbox.index('current').split('.')[0])-1]
            if not selected_line.strip():
                return
                
            service = selected_line.split(" - ")[0]
            
            reply = messagebox.askyesno(
                'Confirm', 
                f"Are you sure you want to delete the password for {service}?"
            )
            
            if reply:
                self.passwords = [p for p in self.passwords if p['service'] != service]
                self.save_passwords()
                self.update_password_list()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a password to delete!")

    def export_passwords(self):
        """Export all passwords to a file"""
        if not self.passwords:
            messagebox.showwarning("Warning", "No passwords to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save passwords to file"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for pwd in self.passwords:
                        f.write(f"Service: {pwd['service']}\n")
                        f.write(f"Username: {pwd['username']}\n")
                        f.write(f"Password: {pwd['password']}\n")
                        f.write("-" * 30 + "\n")
                messagebox.showinfo("Success", "Passwords exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = PasswordManager(root)
    root.mainloop()