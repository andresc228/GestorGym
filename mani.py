from dataclasses import dataclass, field
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import uuid


@dataclass
class Usuario:
    username: str
    password: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Entrenador(Usuario):
    nombre: str = ""
    nivel_experiencia: str = ""
    clientes_ids: List[str] = field(default_factory=list)

@dataclass
class Cliente(Usuario):
    nombre: str = ""
    objetivos: str = ""
    estado_fisico_inicial: str = ""
    entrenador_id: Optional[str] = None
    rutinas_ids: List[str] = field(default_factory=list)
    planes_ids: List[str] = field(default_factory=list)
    progreso_historial: List[str] = field(default_factory=list)

@dataclass
class RutinaEjercicio:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cliente_id: str = ""
    entrenador_id: str = ""
    ejercicios_semana: Dict[str, List[Dict]] = field(default_factory=dict)  # dia -> list ejercicios
    fecha_creacion: str = field(default_factory=lambda: date.today().isoformat())
    intensidad: str = "Media"

@dataclass
class PlanAlimentacion:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cliente_id: str = ""
    comidas_por_dia: int = 3
    calorias_diarias: int = 2000
    detalle_comidas: Dict[str, str] = field(default_factory=dict)  # 'Desayuno': '...'
    fecha_creacion: str = field(default_factory=lambda: date.today().isoformat())
    observaciones: str = ""

@dataclass
class ProgresoFisico:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cliente_id: str = ""
    fecha: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    peso: float = 0.0
    medidas: Dict[str, float] = field(default_factory=dict)
    repeticiones: Dict[str, int] = field(default_factory=dict)
    observaciones: str = ""


class Repositorio:
    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}
        self.entrenadores: Dict[str, Entrenador] = {}
        self.clientes: Dict[str, Cliente] = {}
        self.rutinas: Dict[str, RutinaEjercicio] = {}
        self.planes: Dict[str, PlanAlimentacion] = {}
        self.progresos: Dict[str, ProgresoFisico] = {}


    def add_entrenador(self, ent: Entrenador):
        self.entrenadores[ent.id] = ent
        self.usuarios[ent.id] = ent

    def add_cliente(self, cli: Cliente):
        self.clientes[cli.id] = cli
        self.usuarios[cli.id] = cli


    def vincular_cliente_a_entrenador(self, cliente_id: str, entrenador_id: str):
        cli = self.clientes.get(cliente_id)
        ent = self.entrenadores.get(entrenador_id)
        if not cli or not ent:
            return False

        if cli.entrenador_id and cli.entrenador_id in self.entrenadores:
            prev = self.entrenadores[cli.entrenador_id]
            if cliente_id in prev.clientes_ids:
                prev.clientes_ids.remove(cliente_id)
        cli.entrenador_id = entrenador_id
        if cliente_id not in ent.clientes_ids:
            ent.clientes_ids.append(cliente_id)
        return True


    def crear_plan_automatico(self, cliente_id: str) -> PlanAlimentacion:
        cli = self.clientes.get(cliente_id)
        if not cli:
            raise ValueError("Cliente no encontrado")
        objetivo = (cli.objetivos or "").lower()
        if "fuerza" in objetivo:
            calorias = 2800
            detalle = {
                "Desayuno": "Avena, 3 huevos, banana, leche",
                "Media mañana": "Batido proteína + frutos secos",
                "Almuerzo": "Arroz integral, pollo a la plancha, aguacate, ensalada",
                "Merienda": "Yogur griego + granola",
                "Cena": "Carne magra, papas asadas, vegetales"
            }
            comidas = 5
            obs = "Enfocado en superávit calórico y proteínas para fuerza."
        elif "bajar" in objetivo or "peso" in objetivo:
            calorias = 1700
            detalle = {
                "Desayuno": "Claras revueltas, avena (porción pequeña), manzana",
                "Media mañana": "Yogur natural o té",
                "Almuerzo": "Pechuga de pollo, ensalada abundante, quinoa pequeña",
                "Merienda": "Frutos secos (porción pequeña)",
                "Cena": "Pescado al vapor, vegetales al vapor"
            }
            comidas = 5
            obs = "Déficit moderado con proteína suficiente."
        else:  # salud
            calorias = 2100
            detalle = {
                "Desayuno": "Yogur natural, granola, frutas",
                "Media mañana": "Fruta y nueces",
                "Almuerzo": "Pollo a la plancha, arroz integral, ensalada",
                "Merienda": "Batido de frutas",
                "Cena": "Sopa ligera, pan integral, vegetales"
            }
            comidas = 5
            obs = "Balanceado, enfocado en calidad de alimentos."
        plan = PlanAlimentacion(
            cliente_id=cliente_id,
            comidas_por_dia=comidas,
            calorias_diarias=calorias,
            detalle_comidas=detalle,
            observaciones=obs
        )
        self.planes[plan.id] = plan
        cli.planes_ids.append(plan.id)
        return plan


    def crear_rutina_automatica(self, cliente_id: str, entrenador_id: Optional[str] = None) -> RutinaEjercicio:
        cli = self.clientes.get(cliente_id)
        if not cli:
            raise ValueError("Cliente no encontrado")
        objetivo = (cli.objetivos or "").lower()
        semana = {}
        intensidad = "Media"
        if "fuerza" in objetivo:
            intensidad = "Alta"
            semana = {
                "Lunes": [
                    {"ejercicio": "Press banca", "series": 4, "reps": "6-8"},
                    {"ejercicio": "Fondos", "series": 3, "reps": "6-8"},
                    {"ejercicio": "Press inclinado", "series": 3, "reps": "6-8"}
                ],
                "Martes": [
                    {"ejercicio": "Peso muerto", "series": 4, "reps": "5-6"},
                    {"ejercicio": "Remo con barra", "series": 4, "reps": "6-8"}
                ],
                "Miércoles": [
                    {"ejercicio": "Sentadillas", "series": 4, "reps": "6-8"},
                    {"ejercicio": "Prensa", "series": 3, "reps": "6-8"}
                ],
                "Jueves": [
                    {"ejercicio": "Press militar", "series": 3, "reps": "6-8"},
                    {"ejercicio": "Elevaciones laterales", "series": 3, "reps": "8-10"}
                ],
                "Viernes": [
                    {"ejercicio": "Curl bíceps", "series": 3, "reps": "6-8"},
                    {"ejercicio": "Tríceps polea", "series": 3, "reps": "6-8"}
                ],
                "Sábado": [{"ejercicio": "Cardio ligero", "series": 1, "reps": "20-30 min"}],
                "Domingo": [{"ejercicio": "Descanso", "series": 0, "reps": ""}]
            }
        elif "bajar" in objetivo or "peso" in objetivo:
            intensidad = "Alta"
            semana = {
                "Lunes": [
                    {"ejercicio": "Circuito (sentadillas, flexiones, salto)", "series": 3, "reps": "15-20 cada ejercicio"},
                    {"ejercicio": "Cardio HIIT", "series": 1, "reps": "15-20 min"}
                ],
                "Martes": [
                    {"ejercicio": "Entrenamiento full body", "series": 3, "reps": "12-15"}
                ],
                "Miércoles": [
                    {"ejercicio": "Cardio moderado", "series": 1, "reps": "30-40 min"}
                ],
                "Jueves": [
                    {"ejercicio": "Circuito + core", "series": 3, "reps": "15-20"}
                ],
                "Viernes": [
                    {"ejercicio": "HIIT + fuerza ligera", "series": 3, "reps": "12-15"}
                ],
                "Sábado": [{"ejercicio": "Caminata larga", "series": 1, "reps": "45-60 min"}],
                "Domingo": [{"ejercicio": "Descanso activo (yoga)"}]
            }
        else:
            intensidad = "Baja-Media"
            semana = {
                "Lunes": [
                    {"ejercicio": "Full body ligero", "series": 3, "reps": "10-12"},
                    {"ejercicio": "Caminata", "series": 1, "reps": "30 min"}
                ],
                "Martes": [
                    {"ejercicio": "Movilidad y yoga", "series": 1, "reps": "30-40 min"}
                ],
                "Miércoles": [
                    {"ejercicio": "Entrenamiento funcional", "series": 3, "reps": "10-12"}
                ],
                "Jueves": [
                    {"ejercicio": "Caminata ligera", "series": 1, "reps": "30 min"}
                ],
                "Viernes": [
                    {"ejercicio": "Circuito suave", "series": 3, "reps": "12-15"}
                ],
                "Sábado": [{"ejercicio": "Actividad recreativa", "series": 1, "reps": "60 min"}],
                "Domingo": [{"ejercicio": "Descanso"}]
            }
        rutina = RutinaEjercicio(cliente_id=cliente_id, entrenador_id=entrenador_id or "", ejercicios_semana=semana, intensidad=intensidad)
        self.rutinas[rutina.id] = rutina
        cli.rutinas_ids.append(rutina.id)
        return rutina


    def registrar_progreso(self, progreso: ProgresoFisico):
        self.progresos[progreso.id] = progreso
        cli = self.clientes.get(progreso.cliente_id)
        if cli:
            cli.progreso_historial.append(progreso.id)


    def crear_rutina_personalizada(self, entrenador_id: str, cliente_id: str, ejercicios_semana: Dict[str, List[Dict]], intensidad: str="Personalizada") -> RutinaEjercicio:
        ent = self.entrenadores.get(entrenador_id)
        cli = self.clientes.get(cliente_id)
        if not ent or not cli:
            raise ValueError("Entrenador o cliente no encontrado")

        if cliente_id not in ent.clientes_ids:
            raise PermissionError("Entrenador no está vinculado a este cliente")
        rutina = RutinaEjercicio(cliente_id=cliente_id, entrenador_id=entrenador_id, ejercicios_semana=ejercicios_semana, intensidad=intensidad)
        self.rutinas[rutina.id] = rutina
        cli.rutinas_ids.append(rutina.id)
        return rutina


    def crear_plan_personalizado(self, entrenador_id: str, cliente_id: str, detalle_comidas: Dict[str, str], calorias: int, comidas_por_dia: int, observaciones: str="") -> PlanAlimentacion:
        ent = self.entrenadores.get(entrenador_id)
        cli = self.clientes.get(cliente_id)
        if not ent or not cli:
            raise ValueError("Entrenador o cliente no encontrado")
        if cliente_id not in ent.clientes_ids:
            raise PermissionError("Entrenador no está vinculado a este cliente")
        plan = PlanAlimentacion(cliente_id=cliente_id, comidas_por_dia=comidas_por_dia, calorias_diarias=calorias, detalle_comidas=detalle_comidas, observaciones=observaciones)
        self.planes[plan.id] = plan
        cli.planes_ids.append(plan.id)
        return plan

repo = Repositorio()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Gimnasio")
        self.geometry("1000x650")
        self.resizable(False, False)
        self.usuario_actual: Optional[Usuario] = None


        self.frame_login = FrameLogin(self)
        self.frame_dashboard = FrameDashboard(self)

        self.frame_login.pack(fill="both", expand=True)

    def entrar(self, usuario: Usuario):
        self.usuario_actual = usuario
        self.frame_login.pack_forget()
        self.frame_dashboard.refresh()
        self.frame_dashboard.pack(fill="both", expand=True)

    def salir(self):
        self.usuario_actual = None
        self.frame_dashboard.pack_forget()
        self.frame_login.clear_fields()
        self.frame_login.pack(fill="both", expand=True)


class FrameLogin(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        tk.Label(self, text="Gestor de Gimnasio", font=("Arial", 20)).pack(pady=16)

        frm = tk.Frame(self)
        frm.pack(pady=6)
        tk.Label(frm, text="Usuario:").grid(row=0, column=0, sticky="e", padx=6)
        tk.Label(frm, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=6)
        self.ent_user = tk.Entry(frm, width=30)
        self.ent_pass = tk.Entry(frm, show="*", width=30)
        self.ent_user.grid(row=0, column=1, pady=6)
        self.ent_pass.grid(row=1, column=1, pady=6)

        btns = tk.Frame(self)
        btns.pack(pady=12)
        tk.Button(btns, text="Iniciar sesión", command=self.login, width=18, height=2).pack(side="left", padx=6)
        tk.Button(btns, text="Registrar (cliente/entrenador)", command=self.registrar_usuario_dialog, width=24, height=2).pack(side="left", padx=6)
        tk.Button(btns, text="Salir", command=self.quit, width=10, height=2).pack(side="left", padx=6)

    def clear_fields(self):
        self.ent_user.delete(0, tk.END)
        self.ent_pass.delete(0, tk.END)

    def login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Faltan datos", "Ingrese usuario y contraseña.")
            return
        found = None
        for usr in repo.usuarios.values():
            if usr.username == u and usr.password == p:
                found = usr
                break
        if found:
            messagebox.showinfo("Bienvenido", f"Sesión iniciada: {u}")
            self.master.entrar(found)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def registrar_usuario_dialog(self):
        dlg = RegistroUsuarioDialog(self.master)
        self.wait_window(dlg)


class RegistroUsuarioDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registrar Usuario")
        self.geometry("520x420")
        self.transient(parent)
        self.grab_set()

        self.tipo_var = tk.StringVar(value="cliente")
        tk.Label(self, text="Tipo de usuario", font=("Arial", 12)).pack(pady=6)
        tipo_frame = tk.Frame(self)
        tipo_frame.pack()
        tk.Radiobutton(tipo_frame, text="Cliente", variable=self.tipo_var, value="cliente").pack(side="left", padx=10)
        tk.Radiobutton(tipo_frame, text="Entrenador", variable=self.tipo_var, value="entrenador").pack(side="left", padx=10)

        form = tk.Frame(self)
        form.pack(pady=10, padx=8, fill="x")
        tk.Label(form, text="Nombre completo:").grid(row=0, column=0, sticky="e", pady=6)
        tk.Label(form, text="Usuario (login):").grid(row=1, column=0, sticky="e", pady=6)
        tk.Label(form, text="Contraseña:").grid(row=2, column=0, sticky="e", pady=6)

        self.e_nombre = tk.Entry(form, width=40); self.e_nombre.grid(row=0, column=1, pady=6)
        self.e_user = tk.Entry(form, width=40); self.e_user.grid(row=1, column=1, pady=6)
        self.e_pass = tk.Entry(form, width=40, show="*"); self.e_pass.grid(row=2, column=1, pady=6)


        tk.Label(form, text="Objetivo (clientes):").grid(row=3, column=0, sticky="e", pady=6)
        self.combo_obj = ttk.Combobox(form, values=["Más fuerza", "Bajar de peso", "Salud"], state="readonly", width=37)
        self.combo_obj.grid(row=3, column=1, pady=6)
        self.combo_obj.set("Salud")

        tk.Label(form, text="Estado físico inicial:").grid(row=4, column=0, sticky="e", pady=6)
        self.e_estado = tk.Entry(form, width=40); self.e_estado.grid(row=4, column=1, pady=6)


        tk.Label(form, text="Nivel experiencia (entrenadores):").grid(row=5, column=0, sticky="e", pady=6)
        self.e_nivel = tk.Entry(form, width=40); self.e_nivel.grid(row=5, column=1, pady=6)

        btns = tk.Frame(self)
        btns.pack(pady=12)
        tk.Button(btns, text="Registrar", command=self.registrar, width=14, height=2).pack(side="left", padx=8)
        tk.Button(btns, text="Cancelar", command=self.destroy, width=12, height=2).pack(side="left", padx=8)

    def registrar(self):
        tipo = self.tipo_var.get()
        nombre = self.e_nombre.get().strip()
        user = self.e_user.get().strip()
        pwd = self.e_pass.get().strip()
        if not nombre or not user or not pwd:
            messagebox.showwarning("Datos incompletos", "Complete nombre, usuario y contraseña.")
            return

        for u in repo.usuarios.values():
            if u.username == user:
                messagebox.showerror("Error", "El nombre de usuario ya existe.")
                return
        if tipo == "cliente":
            objetivo = self.combo_obj.get().strip() or "Salud"
            cli = Cliente(username=user, password=pwd, nombre=nombre, objetivos=objetivo, estado_fisico_inicial=self.e_estado.get().strip())
            repo.add_cliente(cli)
            messagebox.showinfo("Cliente registrado", f"Cliente {nombre} registrado correctamente.")
        else:
            ent = Entrenador(username=user, password=pwd, nombre=nombre, nivel_experiencia=self.e_nivel.get().strip())
            repo.add_entrenador(ent)
            messagebox.showinfo("Entrenador registrado", f"Entrenador {nombre} registrado correctamente.")
        self.destroy()


class FrameDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        header = tk.Frame(self)
        header.pack(fill="x", pady=8)
        self.lbl_user = tk.Label(header, text="No autenticado", font=("Arial", 14))
        self.lbl_user.pack(side="left", padx=8)
        tk.Button(header, text="Cerrar sesión", command=self.master.salir, width=12, height=1).pack(side="right", padx=8)

        botones = tk.Frame(self)
        botones.pack(pady=6, fill="x")


        tk.Button(botones, text="Registrar Cliente", width=20, height=2, command=self.registrar_cliente).pack(side="left", padx=6)
        tk.Button(botones, text="Registrar Entrenador", width=20, height=2, command=self.registrar_entrenador).pack(side="left", padx=6)
        tk.Button(botones, text="Vincular Cliente a Entrenador", width=26, height=2, command=self.vincular_cliente).pack(side="left", padx=6)
        tk.Button(botones, text="Crear Plan de Alimentación (auto)", width=26, height=2, command=self.crear_plan_auto).pack(side="left", padx=6)
        tk.Button(botones, text="Crear Rutina (auto)", width=22, height=2, command=self.crear_rutina_auto).pack(side="left", padx=6)
        tk.Button(botones, text="Ver Progreso de Cliente", width=20, height=2, command=self.ver_progreso).pack(side="left", padx=6)


        self.frame_ent_ops = tk.Frame(self)
        self.frame_ent_ops.pack(pady=6)
        tk.Button(self.frame_ent_ops, text="Crear Rutina personalizada (entrenador)", width=30, height=2, command=self.crear_rutina_personalizada).pack(side="left", padx=6)
        tk.Button(self.frame_ent_ops, text="Crear Plan personalizado (entrenador)", width=30, height=2, command=self.crear_plan_personalizado).pack(side="left", padx=6)


        area = tk.Frame(self)
        area.pack(fill="both", expand=True, padx=8, pady=8)

        self.tabs = ttk.Notebook(area)
        self.tab_ent = tk.Frame(self.tabs)
        self.tab_cli = tk.Frame(self.tabs)
        self.tab_rut = tk.Frame(self.tabs)
        self.tab_plan = tk.Frame(self.tabs)
        self.tab_prog = tk.Frame(self.tabs)

        self.tabs.add(self.tab_ent, text="Entrenadores")
        self.tabs.add(self.tab_cli, text="Clientes")
        self.tabs.add(self.tab_rut, text="Rutinas")
        self.tabs.add(self.tab_plan, text="Planes")
        self.tabs.add(self.tab_prog, text="Progresos")
        self.tabs.pack(fill="both", expand=True)


        self.tree_ent = ttk.Treeview(self.tab_ent, columns=("id","nombre","nivel","clientes"), show="headings")
        for c in ("id","nombre","nivel","clientes"):
            self.tree_ent.heading(c, text=c)
        self.tree_ent.pack(fill="both", expand=True)

        self.tree_cli = ttk.Treeview(self.tab_cli, columns=("id","nombre","objetivos","estado","entrenador"), show="headings")
        for c in ("id","nombre","objetivos","estado","entrenador"):
            self.tree_cli.heading(c, text=c)
        self.tree_cli.pack(fill="both", expand=True)

        self.tree_rut = ttk.Treeview(self.tab_rut, columns=("id","cliente","entrenador","fecha","intensidad"), show="headings")
        for c in ("id","cliente","entrenador","fecha","intensidad"):
            self.tree_rut.heading(c, text=c)
        self.tree_rut.pack(fill="both", expand=True)

        self.tree_plan = ttk.Treeview(self.tab_plan, columns=("id","cliente","calorias","comidas","fecha"), show="headings")
        for c in ("id","cliente","calorias","comidas","fecha"):
            self.tree_plan.heading(c, text=c)
        self.tree_plan.pack(fill="both", expand=True)

        self.tree_prog = ttk.Treeview(self.tab_prog, columns=("id","cliente","fecha","peso","obs"), show="headings")
        for c in ("id","cliente","fecha","peso","obs"):
            self.tree_prog.heading(c, text=c)
        self.tree_prog.pack(fill="both", expand=True)

        acciones = tk.Frame(self)
        acciones.pack(pady=6)
        tk.Button(acciones, text="Agregar Progreso (cliente)", width=20, height=2, command=self.agregar_progreso).pack(side="left", padx=6)
        tk.Button(acciones, text="Detalles Cliente", width=18, height=2, command=self.detalles_cliente).pack(side="left", padx=6)

    def refresh(self):
        u = self.master.usuario_actual
        if isinstance(u, Entrenador):
            rol = "Entrenador"
        elif isinstance(u, Cliente):
            rol = "Cliente"
        else:
            rol = "Usuario"
        self.lbl_user.config(text=f"Usuario: {u.username} ({rol})")

        if not isinstance(u, Entrenador):
            self.frame_ent_ops.forget()
        else:

            self.frame_ent_ops.pack(pady=6)
        self._refresh_trees()

    def _refresh_trees(self):
        for t in (self.tree_ent, self.tree_cli, self.tree_rut, self.tree_plan, self.tree_prog):
            for i in t.get_children():
                t.delete(i)
        for ent in repo.entrenadores.values():
            self.tree_ent.insert("", "end", values=(ent.id, ent.nombre, ent.nivel_experiencia, len(ent.clientes_ids)))
        for cli in repo.clientes.values():
            ent_name = repo.entrenadores[cli.entrenador_id].nombre if (cli.entrenador_id and cli.entrenador_id in repo.entrenadores) else ""
            self.tree_cli.insert("", "end", values=(cli.id, cli.nombre, cli.objetivos, cli.estado_fisico_inicial, ent_name))
        for r in repo.rutinas.values():
            ent_name = repo.entrenadores[r.entrenador_id].nombre if r.entrenador_id in repo.entrenadores else r.entrenador_id
            cli_name = repo.clientes[r.cliente_id].nombre if r.cliente_id in repo.clientes else r.cliente_id
            self.tree_rut.insert("", "end", values=(r.id, cli_name, ent_name, r.fecha_creacion, r.intensidad))
        for p in repo.planes.values():
            cli_name = repo.clientes[p.cliente_id].nombre if p.cliente_id in repo.clientes else p.cliente_id
            self.tree_plan.insert("", "end", values=(p.id, cli_name, p.calorias_diarias, p.comidas_por_dia, p.fecha_creacion))
        for pr in repo.progresos.values():
            cli_name = repo.clientes[pr.cliente_id].nombre if pr.cliente_id in repo.clientes else pr.cliente_id
            self.tree_prog.insert("", "end", values=(pr.id, cli_name, pr.fecha, pr.peso, pr.observaciones))


    def registrar_cliente(self):
        dlg = RegistroUsuarioDialog(self.master)
        self.wait_window(dlg)
        self._refresh_trees()

    def registrar_entrenador(self):
        dlg = RegistroUsuarioDialog(self.master)
        self.wait_window(dlg)
        self._refresh_trees()

    def vincular_cliente(self):
        if not repo.clientes:
            messagebox.showwarning("Sin clientes", "No hay clientes registrados.")
            return
        if not repo.entrenadores:
            messagebox.showwarning("Sin entrenadores", "No hay entrenadores registrados.")
            return
        sel_cli = SelectionDialog(self, "Seleccionar Cliente", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel_cli)
        if not sel_cli.selected_id:
            return
        sel_ent = SelectionDialog(self, "Seleccionar Entrenador", [(e.id, e.nombre) for e in repo.entrenadores.values()])
        self.wait_window(sel_ent)
        if not sel_ent.selected_id:
            return
        ok = repo.vincular_cliente_a_entrenador(sel_cli.selected_id, sel_ent.selected_id)
        if ok:
            messagebox.showinfo("Vinculado", "Cliente vinculado correctamente al entrenador.")
            self._refresh_trees()
        else:
            messagebox.showerror("Error", "No se pudo vincular.")

    def crear_plan_auto(self):
        if not repo.clientes:
            messagebox.showwarning("Sin clientes", "No hay clientes registrados.")
            return
        sel = SelectionDialog(self, "Seleccionar Cliente para Plan automático", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel)
        if not sel.selected_id:
            return
        cli = repo.clientes[sel.selected_id]

        if cli.entrenador_id:

            resp = messagebox.askyesno("Cliente con entrenador", "Este cliente tiene entrenador asignado. ¿Deseas crear un plan automático igualmente? (Se recomienda que el entrenador cree uno personalizado).")
            if not resp:
                return
        plan = repo.crear_plan_automatico(sel.selected_id)

        MostrarPlanDialog(self, plan).wait_window()
        self._refresh_trees()

    def crear_rutina_auto(self):
        if not repo.clientes:
            messagebox.showwarning("Sin clientes", "No hay clientes registrados.")
            return
        sel = SelectionDialog(self, "Seleccionar Cliente para Rutina automática", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel)
        if not sel.selected_id:
            return
        cli = repo.clientes[sel.selected_id]
        if cli.entrenador_id:
            resp = messagebox.askyesno("Cliente con entrenador", "Este cliente tiene entrenador asignado. ¿Deseas crear una rutina automática igualmente? (Se recomienda que el entrenador cree una personalizada).")
            if not resp:
                return
        rutina = repo.crear_rutina_automatica(sel.selected_id, cli.entrenador_id)
        MostrarRutinaDialog(self, rutina).wait_window()
        self._refresh_trees()

    def ver_progreso(self):
        if not repo.clientes:
            messagebox.showwarning("Sin clientes", "No hay clientes registrados.")
            return
        sel = SelectionDialog(self, "Seleccionar Cliente para ver Progreso", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel)
        if not sel.selected_id:
            return
        cliente = repo.clientes[sel.selected_id]
        dlg = VerProgresoDialog(self, cliente)
        self.wait_window(dlg)

    def agregar_progreso(self):
        if not repo.clientes:
            messagebox.showwarning("Sin clientes", "No hay clientes registrados.")
            return
        sel = SelectionDialog(self, "Seleccionar Cliente para agregar Progreso", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel)
        if not sel.selected_id:
            return
        cliente = repo.clientes[sel.selected_id]
        peso = simpledialog.askfloat("Peso", "Ingrese peso (kg):", parent=self, minvalue=0.0)
        if peso is None:
            return
        obs = simpledialog.askstring("Observaciones", "Observaciones (opcional):", parent=self)
        medidas = {}
        m_cint = simpledialog.askfloat("Medida - cintura (cm)", "Cintura (cm):", parent=self, minvalue=0.0)
        if m_cint is not None:
            medidas["cintura"] = m_cint
        prog = ProgresoFisico(cliente_id=cliente.id, peso=peso, medidas=medidas, observaciones=obs or "")
        repo.registrar_progreso(prog)
        messagebox.showinfo("Registrado", "Progreso registrado correctamente.")
        self._refresh_trees()

    def detalles_cliente(self):
        sel = SelectionDialog(self, "Seleccionar Cliente para Detalles", [(c.id, c.nombre) for c in repo.clientes.values()])
        self.wait_window(sel)
        if not sel.selected_id:
            return
        cli = repo.clientes[sel.selected_id]
        textos = []
        textos.append(f"Nombre: {cli.nombre}")
        textos.append(f"Objetivo: {cli.objetivos}")
        textos.append(f"Estado inicial: {cli.estado_fisico_inicial}")
        textos.append(f"Entrenador: {repo.entrenadores[cli.entrenador_id].nombre if (cli.entrenador_id and cli.entrenador_id in repo.entrenadores) else 'No asignado'}")
        textos.append(f"Rutinas: {len(cli.rutinas_ids)}")
        textos.append(f"Planes: {len(cli.planes_ids)}")
        fechas = []
        for pid in cli.progreso_historial:
            p = repo.progresos.get(pid)
            if p:
                try:
                    fechas.append(datetime.strptime(p.fecha, "%Y-%m-%d %H:%M:%S").date())
                except:
                    pass
        for rid in cli.rutinas_ids:
            r = repo.rutinas.get(rid)
            if r:
                try:
                    fechas.append(datetime.fromisoformat(r.fecha_creacion).date())
                except:
                    pass
        for plid in cli.planes_ids:
            pl = repo.planes.get(plid)
            if pl:
                try:
                    fechas.append(datetime.fromisoformat(pl.fecha_creacion).date())
                except:
                    pass
        if fechas:
            primera = min(fechas)
            dias = (date.today() - primera).days
            textos.append(f"Tiempo entrenando (aprox): {dias} días (desde {primera.isoformat()})")
        else:
            textos.append("Tiempo entrenando: Sin registros aún.")
        pesos = []
        for pid in cli.progreso_historial:
            p = repo.progresos.get(pid)
            if p and p.peso:
                pesos.append((p.fecha, p.peso))
        if len(pesos) >= 2:
            pesos_sorted = sorted(pesos, key=lambda x: x[0])
            cambio = pesos_sorted[-1][1] - pesos_sorted[0][1]
            textos.append(f"Cambio de peso desde primer control: {cambio:+.2f} kg")
        elif len(pesos) == 1:
            textos.append("Sólo hay un registro de peso — no es posible evaluar tendencia aún.")
        else:
            textos.append("No hay registros de peso.")
        messagebox.showinfo("Detalles del Cliente", "\n".join(textos))


    def crear_rutina_personalizada(self):
        # Solo visible/usable si usuario actual es entrenador
        if not isinstance(self.master.usuario_actual, Entrenador):
            messagebox.showerror("Acceso denegado", "Sólo los entrenadores pueden crear rutinas personalizadas.")
            return
        ent = self.master.usuario_actual
        if not ent.clientes_ids:
            messagebox.showwarning("Sin clientes vinculados", "No tienes clientes vinculados.")
            return

        opciones = [(cid, repo.clientes[cid].nombre) for cid in ent.clientes_ids if cid in repo.clientes]
        sel = SelectionDialog(self, "Seleccionar cliente (para rutina personalizada)", opciones)
        self.wait_window(sel)
        if not sel.selected_id:
            return
        dlg = RutinaPersonalizadaDialog(self, ent, repo.clientes[sel.selected_id])
        self.wait_window(dlg)
        if dlg.result:
            ejercicios_semana, intensidad = dlg.result
            try:
                rutina = repo.crear_rutina_personalizada(ent.id, sel.selected_id, ejercicios_semana, intensidad=intensidad)
                MostrarRutinaDialog(self, rutina).wait_window()
                self._refresh_trees()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def crear_plan_personalizado(self):
        if not isinstance(self.master.usuario_actual, Entrenador):
            messagebox.showerror("Acceso denegado", "Sólo los entrenadores pueden crear planes personalizados.")
            return
        ent = self.master.usuario_actual
        if not ent.clientes_ids:
            messagebox.showwarning("Sin clientes vinculados", "No tienes clientes vinculados.")
            return
        opciones = [(cid, repo.clientes[cid].nombre) for cid in ent.clientes_ids if cid in repo.clientes]
        sel = SelectionDialog(self, "Seleccionar cliente (para plan personalizado)", opciones)
        self.wait_window(sel)
        if not sel.selected_id:
            return
        dlg = PlanPersonalizadoDialog(self, ent, repo.clientes[sel.selected_id])
        self.wait_window(dlg)
        if dlg.result:
            detalle_comidas, calorias, comidas_por_dia, observaciones = dlg.result
            try:
                plan = repo.crear_plan_personalizado(ent.id, sel.selected_id, detalle_comidas, calorias, comidas_por_dia, observaciones)
                MostrarPlanDialog(self, plan).wait_window()
                self._refresh_trees()
            except PermissionError as pe:
                messagebox.showerror("Permiso", str(pe))
            except Exception as e:
                messagebox.showerror("Error", str(e))


class SelectionDialog(tk.Toplevel):
    def __init__(self, parent, title, opciones):
        super().__init__(parent)
        self.title(title)
        self.geometry("480x360")
        self.transient(parent)
        self.grab_set()
        self.selected_id = None
        tk.Label(self, text=title, font=("Arial", 12)).pack(pady=8)
        self.tree = ttk.Treeview(self, columns=("id","nombre"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        for id_, nom in opciones:
            self.tree.insert("", "end", values=(id_, nom))
        btns = tk.Frame(self)
        btns.pack(pady=6)
        tk.Button(btns, text="Seleccionar", command=self.seleccionar, width=12, height=2).pack(side="left", padx=6)
        tk.Button(btns, text="Cancelar", command=self.destroy, width=10, height=2).pack(side="left", padx=6)

    def seleccionar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nada seleccionado", "Seleccione un elemento.")
            return
        vals = self.tree.item(sel[0], "values")
        self.selected_id = vals[0]
        self.destroy()


class MostrarRutinaDialog(tk.Toplevel):
    def __init__(self, parent, rutina: RutinaEjercicio):
        super().__init__(parent)
        self.title(f"Rutina - {repo.clientes[rutina.cliente_id].nombre if rutina.cliente_id in repo.clientes else rutina.cliente_id}")
        self.geometry("700x520")
        self.transient(parent)
        self.grab_set()

        lbl = tk.Label(self, text=f"Rutina (intensidad: {rutina.intensidad})", font=("Arial", 12))
        lbl.pack(pady=6)

        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)
        txt = tk.Text(frm, wrap="word")
        sb = ttk.Scrollbar(frm, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        contenido = []
        for dia, ejercicios in rutina.ejercicios_semana.items():
            contenido.append(f"{dia}:\n")
            for ex in ejercicios:
                line = f"  - {ex.get('ejercicio')}: {ex.get('series')} x {ex.get('reps')}\n"
                contenido.append(line)
            contenido.append("\n")
        txt.insert("1.0", "".join(contenido))
        txt.config(state="disabled")
        tk.Button(self, text="Cerrar", command=self.destroy, width=12, height=2).pack(pady=6)


class MostrarPlanDialog(tk.Toplevel):
    def __init__(self, parent, plan: PlanAlimentacion):
        super().__init__(parent)
        cliente_nom = repo.clientes[plan.cliente_id].nombre if plan.cliente_id in repo.clientes else plan.cliente_id
        self.title(f"Plan - {cliente_nom}")
        self.geometry("700x520")
        self.transient(parent)
        self.grab_set()

        lbl = tk.Label(self, text=f"Plan de Alimentación - {plan.calorias_diarias} kcal", font=("Arial", 12))
        lbl.pack(pady=6)
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)
        txt = tk.Text(frm, wrap="word")
        sb = ttk.Scrollbar(frm, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        contenido = [f"Calorías diarias: {plan.calorias_diarias}\nComidas por día: {plan.comidas_por_dia}\n\n"]
        for k, v in plan.detalle_comidas.items():
            contenido.append(f"{k}: {v}\n")
        if plan.observaciones:
            contenido.append(f"\nObservaciones:\n{plan.observaciones}\n")
        txt.insert("1.0", "".join(contenido))
        txt.config(state="disabled")
        tk.Button(self, text="Cerrar", command=self.destroy, width=12, height=2).pack(pady=6)


class VerProgresoDialog(tk.Toplevel):
    def __init__(self, parent, cliente: Cliente):
        super().__init__(parent)
        self.title(f"Progreso - {cliente.nombre}")
        self.geometry("720x460")
        self.transient(parent)
        self.grab_set()
        tk.Label(self, text=f"Historial de progreso - {cliente.nombre}", font=("Arial", 12)).pack(pady=6)
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)
        tree = ttk.Treeview(frm, columns=("fecha","peso","medidas","obs"), show="headings")
        for c in ("fecha","peso","medidas","obs"):
            tree.heading(c, text=c)
        tree.pack(fill="both", expand=True)
        for pid in cliente.progreso_historial:
            p = repo.progresos.get(pid)
            if p:
                medidas_text = ", ".join([f"{k}:{v}" for k,v in p.medidas.items()]) if p.medidas else ""
                tree.insert("", "end", values=(p.fecha, p.peso, medidas_text, p.observaciones))
        tk.Button(self, text="Cerrar", command=self.destroy, width=12, height=2).pack(pady=6)


class RutinaPersonalizadaDialog(tk.Toplevel):
    def __init__(self, parent, entrenador: Entrenador, cliente: Cliente):
        super().__init__(parent)
        self.title(f"Crear Rutina personalizada - Entrenador: {entrenador.nombre} -> Cliente: {cliente.nombre}")
        self.geometry("820x560")
        self.transient(parent)
        self.grab_set()
        self.result = None

        tk.Label(self, text="Crear Rutina Personalizada (rellenar por días)", font=("Arial", 12)).pack(pady=6)

        frm_top = tk.Frame(self)
        frm_top.pack(pady=4)
        tk.Label(frm_top, text="Intensidad:").pack(side="left")
        self.cmb_int = ttk.Combobox(frm_top, values=["Baja", "Media", "Alta", "Personalizada"], state="readonly", width=15)
        self.cmb_int.pack(side="left", padx=6)
        self.cmb_int.set("Personalizada")

        tab_parent = ttk.Notebook(self)
        dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        self.textareas = {}
        self.ejercicios_data = {d: [] for d in dias}
        for d in dias:
            frame = tk.Frame(tab_parent)
            tab_parent.add(frame, text=d)

            tree = ttk.Treeview(frame, columns=("ejercicio","series","reps","nota"), show="headings", height=10)
            for c, h in [("ejercicio","Ejercicio"),("series","Series"),("reps","Reps"),("nota","Nota")]:
                tree.heading(c, text=h)
                tree.column(c, width=150)
            tree.pack(fill="both", expand=True, padx=6, pady=6)
            self.textareas[d] = tree

            addfrm = tk.Frame(frame)
            addfrm.pack(fill="x", pady=4, padx=6)
            self.ej_name = tk.Entry(addfrm, width=25); self.ej_name.pack(side="left", padx=4)
            self.ej_name.insert(0, "Nombre ejercicio")
            self.ej_series = tk.Entry(addfrm, width=8); self.ej_series.pack(side="left", padx=4)
            self.ej_series.insert(0, "3")
            self.ej_reps = tk.Entry(addfrm, width=10); self.ej_reps.pack(side="left", padx=4)
            self.ej_reps.insert(0, "10-12")
            self.ej_note = tk.Entry(addfrm, width=20); self.ej_note.pack(side="left", padx=4)
            self.ej_note.insert(0, "Opcional")

            def make_add(day):
                def add():
                    nombre = self.ej_name.get().strip()
                    series = self.ej_series.get().strip()
                    reps = self.ej_reps.get().strip()
                    nota = self.ej_note.get().strip()
                    if not nombre:
                        messagebox.showwarning("Faltan datos", "Ingrese nombre del ejercicio.")
                        return
                    self.textareas[day].insert("", "end", values=(nombre, series, reps, nota))
                return add
            b = tk.Button(addfrm, text="Agregar ejercicio", command=make_add(d), width=16)
            b.pack(side="left", padx=6)

            def make_del(day):
                def delete():
                    sel = self.textareas[day].selection()
                    if not sel:
                        messagebox.showwarning("Nada seleccionado", "Selecciona una fila para eliminar.")
                        return
                    for s in sel:
                        self.textareas[day].delete(s)
                return delete
            tk.Button(addfrm, text="Eliminar seleccionado", command=make_del(d), width=18).pack(side="left", padx=6)

        tab_parent.pack(fill="both", expand=True, padx=8, pady=8)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        tk.Button(btns, text="Crear rutina y guardar", command=self.crear, width=18, height=2).pack(side="left", padx=6)
        tk.Button(btns, text="Cancelar", command=self.destroy, width=12, height=2).pack(side="left", padx=6)

    def crear(self):

        ejercicios_semana = {}
        for dia, tree in self.textareas.items():
            filas = []
            for iid in tree.get_children():
                vals = tree.item(iid, "values")
                filas.append({"ejercicio": vals[0], "series": vals[1], "reps": vals[2], "nota": vals[3]})
            ejercicios_semana[dia] = filas
        intensidad = self.cmb_int.get() or "Personalizada"
        self.result = (ejercicios_semana, intensidad)
        self.destroy()


class PlanPersonalizadoDialog(tk.Toplevel):
    def __init__(self, parent, entrenador: Entrenador, cliente: Cliente):
        super().__init__(parent)
        self.title(f"Crear Plan personalizado - {entrenador.nombre} -> {cliente.nombre}")
        self.geometry("780x520")
        self.transient(parent)
        self.grab_set()
        self.result = None

        tk.Label(self, text="Plan personalizado (complete comidas)", font=("Arial", 12)).pack(pady=6)
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=6)


        top = tk.Frame(frm)
        top.pack(fill="x", pady=4)
        tk.Label(top, text="Calorías totales:").pack(side="left")
        self.e_cal = tk.Entry(top, width=10); self.e_cal.pack(side="left", padx=6)
        self.e_cal.insert(0, "2000")
        tk.Label(top, text="Comidas por día:").pack(side="left", padx=10)
        self.e_com = tk.Entry(top, width=6); self.e_com.pack(side="left", padx=6)
        self.e_com.insert(0, "5")


        self.comidas = {}
        labels = ["Desayuno","Media mañana","Almuerzo","Merienda","Cena"]
        for lab in labels:
            sub = tk.Frame(frm)
            sub.pack(fill="x", pady=4)
            tk.Label(sub, text=f"{lab}:", width=14, anchor="w").pack(side="left")
            txt = tk.Text(sub, height=3)
            txt.pack(side="left", fill="x", expand=True, padx=6)
            self.comidas[lab] = txt

        tk.Label(frm, text="Observaciones:").pack(anchor="w", pady=4)
        self.txt_obs = tk.Text(frm, height=4)
        self.txt_obs.pack(fill="both", expand=False, padx=8)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        tk.Button(btns, text="Crear plan y guardar", command=self.crear, width=18, height=2).pack(side="left", padx=6)
        tk.Button(btns, text="Cancelar", command=self.destroy, width=12, height=2).pack(side="left", padx=6)

    def crear(self):
        try:
            calorias = int(self.e_cal.get().strip())
        except:
            messagebox.showwarning("Dato inválido", "Ingrese un número válido de calorías.")
            return
        try:
            comidas_por_dia = int(self.e_com.get().strip())
        except:
            messagebox.showwarning("Dato inválido", "Ingrese número válido de comidas por día.")
            return
        detalle = {}
        for lab, txt in self.comidas.items():
            detalle[lab] = txt.get("1.0", "end").strip() or "-"
        obs = self.txt_obs.get("1.0", "end").strip()
        self.result = (detalle, calorias, comidas_por_dia, obs)
        self.destroy()


if __name__ == "__main__":

    if not repo.entrenadores and not repo.clientes:
        ent = Entrenador(username="ent1", password="1234", nombre="Carlos Perez", nivel_experiencia="Senior")
        repo.add_entrenador(ent)
        cli = Cliente(username="cli1", password="1234", nombre="Ana Gomez", objetivos="Bajar de peso", estado_fisico_inicial="Sobrepeso")
        repo.add_cliente(cli)
    app = App()
    app.mainloop()
