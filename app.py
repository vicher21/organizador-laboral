import streamlit as st
import sqlite3
from datetime import date

# ================= CONFIG =================
st.set_page_config(page_title="Organizador Laboral", layout="wide")

# ================= DB =================
conn = sqlite3.connect("tareas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    tema TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    descripcion TEXT,
    categoria TEXT,
    prioridad TEXT,
    fecha_limite TEXT,
    completada INTEGER DEFAULT 0
)
""")
conn.commit()

# ================= CSS =================
with open("girly.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ================= SESSION =================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ================= LOGIN =================
if st.session_state.usuario is None:
    st.markdown("""
        <div class="login-wrapper">
            <div class="login-card">
                <h1>✨ Organizador Laboral ✨</h1>
                <p>Organiza tu día con calma 💖</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    nombre = st.text_input("", placeholder="Tu nombre ✨")

    if st.button("Entrar 💕"):
        cursor.execute("SELECT id, nombre FROM usuarios WHERE nombre=?", (nombre,))
        user = cursor.fetchone()

        if user:
            st.session_state.usuario = {"id": user[0], "nombre": user[1]}
        else:
            cursor.execute(
                "INSERT INTO usuarios (nombre, tema) VALUES (?,?)",
                (nombre, "girly")
            )
            conn.commit()
            st.session_state.usuario = {
                "id": cursor.lastrowid,
                "nombre": nombre
            }
        st.rerun()

    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(f"### 💖 Hola, {st.session_state.usuario['nombre']}")
    if st.button("Cerrar sesión"):
        st.session_state.usuario = None
        st.rerun()

# ================= AGREGAR TAREA (COMPACTO) =================
st.markdown("### ➕ Nueva tarea")

st.markdown("<div class='agregar-tarea-wrapper'>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([4,1.5,1.5,1.5,1])

with col1:
    descripcion = st.text_input(
        "",
        placeholder="Ej: Revisar planilla…",
        label_visibility="collapsed"
    )

with col2:
    categoria = st.selectbox(
        "",
        ["Reunión", "Planillas", "Casos", "Pendientes"],
        label_visibility="collapsed"
    )

with col3:
    prioridad = st.selectbox(
        "",
        ["⭐ Baja", "⭐⭐ Media", "⭐⭐⭐ Alta"],
        label_visibility="collapsed"
    )

with col4:
    fecha = st.date_input(
        "",
        value=date.today(),
        label_visibility="collapsed"
    )

with col5:
    if st.button("＋", key="btn_agregar"):
        if descripcion.strip():
            cursor.execute("""
                INSERT INTO tareas
                (usuario_id, descripcion, categoria, prioridad, fecha_limite)
                VALUES (?,?,?,?,?)
            """, (
                st.session_state.usuario["id"],
                descripcion,
                categoria,
                prioridad,
                fecha.isoformat()
            ))
            conn.commit()
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ================= LISTAS =================
st.markdown("## 📋 Mis tareas")

categorias = ["Reunión", "Planillas", "Casos", "Pendientes"]
cols = st.columns(4)

for col, cat in zip(cols, categorias):
    with col:
        st.markdown(f"### {cat}")

        cursor.execute("""
            SELECT id, descripcion, prioridad, fecha_limite
            FROM tareas
            WHERE usuario_id=? AND categoria=? AND completada=0
            ORDER BY fecha_limite
        """, (st.session_state.usuario["id"], cat))

        tareas = cursor.fetchall()

        if not tareas:
            st.markdown("<div class='vacio'>Nada pendiente ✨</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='contador'>{len(tareas)} tareas</div>",
                unsafe_allow_html=True
            )

            for tid, desc, pri, fecha in tareas:
                c1, c2 = st.columns([0.12, 0.88])

                with c1:
                    if st.button("✔", key=f"done_{tid}"):
                        cursor.execute(
                            "UPDATE tareas SET completada=1 WHERE id=?",
                            (tid,)
                        )
                        conn.commit()
                        st.rerun()

                with c2:
                    st.markdown(f"""
                        <div class="tarea {cat.lower()}">
                            <strong>{desc}</strong><br>
                            <span>{pri}</span><br>
                            <small>📅 {fecha}</small>
                        </div>
                    """, unsafe_allow_html=True)

