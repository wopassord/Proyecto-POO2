import csv
import secrets
from datetime import datetime


class GestionUsuarios:
    def __init__(self, archivo_csv="usuarios.csv"):
        self.archivo_csv = archivo_csv

    def registrar_usuario(self, username, password):
        data = [username, password, self.generar_token()]
        with open(self.archivo_csv, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        return data

    def verificar_usuario(self, username, password):
        with open(self.archivo_csv, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username and row[1] == password:
                    return row
        return None

    def generar_token(self):
        return secrets.token_hex(16)

    def persistir_token(self, username, password, token):
        with open(self.archivo_csv, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, password, token])

    def find_token(self, token):
        with open(self.archivo_csv, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[2] == token:
                    return True
        return False

    def find_user(self, token):
        with open(self.archivo_csv, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[2] == token:
                    return row
        return None
