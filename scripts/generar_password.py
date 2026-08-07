"""
Genera un hash bcrypt para una contraseña nueva.
Uso: python scripts/generar_password.py
"""
import bcrypt

print("=== Generador de contraseña — ETC 88 ===\n")
usuario   = input("Nombre de usuario (ej: leo): ").strip()
password  = input("Nueva contraseña: ").strip()

if not password:
    print("Error: contraseña vacía.")
    exit(1)

hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

print(f"\nPega esto en .streamlit/secrets.toml y en Streamlit Cloud → Secrets:\n")
print(f"[auth.credentials.usernames.{usuario}]")
print(f'name     = "..."  # nombre del usuario')
print(f'password = "{hash_pw}"')
print(f"\nLuego comunica la contraseña '{password}' al usuario por mensaje privado.")
print("¡No guardes este script con la contraseña visible!")
