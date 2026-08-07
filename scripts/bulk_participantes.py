"""
Bulk insert 50 participantes al Sheet.
Uso: python scripts/bulk_participantes.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import get_sheet

PARTICIPANTES = [
    ("Roanny Segueri",                        "Paul"),
    ("Didier Andres Medina Guerrero",          "Paul"),
    ("Sara Olivares",                          "Paul"),
    ("Cristofer Severino",                     "Sor Angelina Lebrón"),
    ("Dahiony Argentina Ortiz Severino",       "Sor Angelina Lebrón"),
    ("Luis Jenner Gonzalez Abreu",             "Rocadis Rodriguez"),
    ("Sorianela Soriano",                      "Phillip Aquino"),
    ("Amanda Arger Rivera Verdia",             "Pamela Colón"),
    ("Diomeiry Vásquez Reyes",                 "Merkin Jean Vásquez"),
    ("Parmenia María Morales Aybar",           "Nelson Morales"),
    ("Lusiany Miguelina Castillo Martínez",    "Olanlly"),
    ("Karen Berroa Santana",                   "Brianelis"),
    ("Yiraimy Núñez Ozoria",                   "Kelvin Alexis Ventura Santana"),
    ("Nicole Benítez",                         "Fernando Cordero"),
    ("Jasiris Moracher",                       "Candy Gatwood"),
    ("Marianne Beltre Castro",                 "Franklin Silverio"),
    ("Cesar Saury Santana Salas",              "Dayrelins Jazmin"),
    ("Hemerson David Asencio Pacheco",         "Leober Carrion Soriano"),
    ("Indiana Garcia",                         "Paloma Mendez"),
    ("Itzel Valenzuela Zorrilla",              "Luisa Maria Fiorentino Brugal"),
    ("Yoandra Rambalde Robles",                "Oliver De León"),
    ("Ashley Charleny Del Jesús Mejia",        "Zahir Valoy"),
    ("Boris Omar Novas Piña",                  "Jonathan Medina"),
    ("Emiliano Enmanuel Vásquez Figueroa",     "Roberto Figueroa"),
    ("Arisleidy Giselle Santana Puente",       "Adrián Francisco Santana Puente"),
    ("Raymin Altagracia Rivera Tavarez",       "Wirna"),
    ("Laura Gabriela Almeida Tavarez",         "Johanny García"),
    ("Dianna Mariel Constanzo Ramos",          "Ismarie"),
    ("Pedro Yunior Peguero Peña",              "Ambar"),
    ("Yorkenys Rodriguez Avila",               "Darianny"),
    ("Yarlenis Faviola Peralta Linarez",       "Chantal"),
    ("Mayerli Elisabet Tejeda Byas",           "Dorian"),
    ("Gianna Geronimo",                        "Victoria"),
    ("Tomas Elías Mercedes Sosa",              "Ivanna"),
    ("Digna Ally Guzmán de la Cruz",           "Roselyn"),
    ("Anderson Rafael Medina Suarez",          "Bethsy Ramírez"),
    ("Víctor Junior Gómez Calderón",           "Erika Gómez"),
    ("Melanie Alejandra Robles Calderón",      "Yafreisy Mesido"),
    ("Pedro José Montero Tavarez",             "Perla Solange Jiménez Trinidad"),
    ("Erilis Daniela Polanco Morales",         "Ricaira Santana"),
    ("Misael Mejia Guerrero",                  "Kirina Humphreys"),
    ("Kevin Sebastián Concepción Martínez",    "Sophia García Fernández"),
    ("Alexandra Marina Gómez",                "Avril Geronimo"),
    ("Doralis Yohana Abreu Carrion",           "Darianny"),
    ("Jefferson Payano del Río",               "Chantal"),
    ("Carmen Angelica Rodriguez Diaz",         "Dorian"),
    ("Cristina María Matos Mercedes",          "Ivanna"),
    ("Juan Alejandro González de la Rosa",     "Roselyn"),
    ("Hilary Marlene Vásquez Telleria",        "Ambar"),
    ("Darivid Eduviges Guzmán Sánchez",        "Ismarie"),
]

def main():
    ws = get_sheet().worksheet("Participantes")
    col_a = ws.col_values(1)
    next_row = len(col_a) + 1

    rows = []
    for i, (nombre, invitado_por) in enumerate(PARTICIPANTES):
        r = next_row + i
        rows.append([
            nombre,
            "",   # Telefono vacío
            f"=IF(A{r}=\"\",\"\",SUMIF('Pagos Participantes'!$A$2:$A$500,A{r},'Pagos Participantes'!$C$2:$C$500))",
            f"=IF(A{r}=\"\",\"\",IF(Resumen!$B$4=0,\"Definir cuota\",IF(C{r}>=Resumen!$B$4,\"PAGO COMPLETO\",\"PENDIENTE\")))",
            "TRUE",
            invitado_por,
        ])

    end_row = next_row + len(rows) - 1
    ws.update(
        values=rows,
        range_name=f"A{next_row}:F{end_row}",
        value_input_option="USER_ENTERED",
    )
    print(f"✓ {len(rows)} participantes insertados (filas {next_row}–{end_row})")

if __name__ == "__main__":
    main()
