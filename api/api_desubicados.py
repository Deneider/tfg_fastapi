from fastapi import FastAPI, Depends, APIRouter, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy import Date, DateTime
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
# Configuración de la base de datos de DesUbicados
SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://diego:diego123@localhost/desubicados"

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la clase base para los modelos
Base = declarative_base()

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Crear el router de esta API
api_desubicados = APIRouter()


# Dependencia para obtennr la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Modelo de SQLAlchemy para Trabajadores
class Trabajadores(Base):
    __tablename__ = 'Trabajadores'

    id_trabajador = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=True)
    fecha_nacimiento = Column(Date, nullable=False)
    dni = Column(String(9), unique=True, nullable=False)
    calle = Column(String(100), nullable=False)
    numero_casa = Column(String(10), nullable=False)
    localidad = Column(String(50), nullable=False)
    provincia = Column(String(50), nullable=False)
    cod_postal = Column(String(10), nullable=False)
    nacionalidad = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    puesto = Column(String(255), nullable=False)


# Ruta para obtener todos los trabajadores
@api_desubicados.get("/Trabajadores")
def get_trabajadores(db: Session = Depends(get_db)):
    trabajadores = db.query(Trabajadores).all()
    return [
        {
            "id_trabajador": t.id_trabajador,
            "nombre": t.nombre,
            "primer_apellido": t.primer_apellido,
            "segundo_apellido": t.segundo_apellido,
            "fecha_nacimiento": t.fecha_nacimiento,
            "dni": t.dni,
            "calle": t.calle,
            "numero_casa": t.numero_casa,
            "localidad": t.localidad,
            "provincia": t.provincia,
            "cod_postal": t.cod_postal,
            "nacionalidad": t.nacionalidad,
            "correo": t.correo,
            "contrasena": t.contrasena,
            "puesto": t.puesto,
        }
        #Bucle mostrar todos los trabajadores y los campos anteriores correspodientes 
        for t in trabajadores 
    ]

# Ruta para obtener un trabajador por correo NUEVO
@api_desubicados.get("/Trabajadores/correo/")
def get_trabajador_por_correo(correo: str = Query(...), db: Session = Depends(get_db)):

    trabajador = db.query(Trabajadores).filter(Trabajadores.correo.like(correo)).first()

    if trabajador is None:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    return trabajador
    

# Modelo Pydantic para la creación de un trabajador
class TrabajadorCreate(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: str
    dni: str
    calle: str
    numero_casa: str
    localidad: str
    provincia: str
    cod_postal: str
    nacionalidad: str
    correo: str
    contrasena: str
    puesto: str
#METODO CREA TRABAJADORES
@api_desubicados.post("/Trabajadores/crear")
def create_trabajador(trabajador: TrabajadorCreate, db: Session = Depends(get_db)):
    try:
        # Convertir la fecha de nacimiento a formato correcto, ya que si no mysql no recoge la información y devuelve error
        fecha_nacimiento = datetime.strptime(trabajador.fecha_nacimiento, '%d-%m-%Y').strftime('%Y-%m-%d')

        nuevo_trabajador = Trabajadores(
            nombre=trabajador.nombre,
            primer_apellido=trabajador.primer_apellido,
            segundo_apellido=trabajador.segundo_apellido,
            fecha_nacimiento=fecha_nacimiento,  # Fecha en el formato correcto
            dni=trabajador.dni,
            calle=trabajador.calle,
            numero_casa=trabajador.numero_casa,
            localidad=trabajador.localidad,
            provincia=trabajador.provincia,
            cod_postal=trabajador.cod_postal,
            nacionalidad=trabajador.nacionalidad,
            correo=trabajador.correo,
            contrasena=trabajador.contrasena,
            puesto=trabajador.puesto
        )
        #Añade el nuevo trabajador con la información anterior
        db.add(nuevo_trabajador)
        db.commit()
        db.refresh(nuevo_trabajador)
        #Si crea el trabajador correctamente devuelve lo siguiente : (id_trabajador se crea de forma automatica en mysql ya que es autoincremental)
        return {"mensaje": "Trabajador creado correctamente", "id_trabajador": nuevo_trabajador.id_trabajador}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

#BORRAR TRABAJADOR
@api_desubicados.delete("/Trabajadores/borrar/")
def delete_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    # Buscar el cliente por ID
    trabajador = db.query(Trabajadores).filter(Trabajadores.id_trabajador == id_trabajador).first()

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    # Eliminar el cliente
    db.delete(trabajador)
    db.commit()

    return {"mensaje": "Trabajador eliminado correctamente", "id_trabajador": id_trabajador}


#Modificar trabajadores 
class TrabajadorUpdate(BaseModel):
    nombre: Optional[str]
    primer_apellido: Optional[str]
    segundo_apellido: Optional[str]
    fecha_nacimiento: Optional[str]  # Formato: 'dd-mm-YYYY'
    dni: Optional[str]
    calle: Optional[str]
    numero_casa: Optional[str]
    localidad: Optional[str]
    provincia: Optional[str]
    cod_postal: Optional[str]
    nacionalidad: Optional[str]
    correo: Optional[str]
    contrasena: Optional[str]
    puesto: Optional[str]

@api_desubicados.put("/Trabajadores/modificar/")
def update_trabajador(id_trabajador: int, datos: TrabajadorUpdate, db: Session = Depends(get_db)):
    trabajador = db.query(Trabajadores).filter(Trabajadores.id_trabajador == id_trabajador).first()

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    try:
        for campo, valor in datos.dict(exclude_unset=True).items():
            if campo == "fecha_nacimiento":
                try:
                    # Convierte de "dd-mm-YYYY" a "YYYY-mm-dd"
                    valor = datetime.strptime(valor, '%d-%m-%Y').strftime('%Y-%m-%d')
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa dd-mm-YYYY.")
            setattr(trabajador, campo, valor)

        db.commit()
        db.refresh(trabajador)

        return {
            "mensaje": "Trabajador actualizado correctamente",
            "id_trabajador": trabajador.id_trabajador
        }

    except HTTPException:
        raise  # Propaga errores lanzados explícitamente
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar trabajador: {str(e)}")

#Modelo SQAlcghemy para Clientes
class Clientes(Base):
    __tablename__ = 'Clientes'

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=True)
    fecha_nacimiento = Column(Date, nullable=False)
    dni = Column(String(9), unique=True, nullable=False)
    calle = Column(String(100), nullable=False)
    numero_casa = Column(String(10), nullable=False)
    localidad = Column(String(50), nullable=False)
    provincia = Column(String(50), nullable=False)
    cod_postal = Column(String(10), nullable=False)
    nacionalidad = Column(String(50), nullable=False)
    puntos = Column(Integer, default=0)  # Sistema de puntos para pagos
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    
    relojes = relationship('Clientes_Relojes', back_populates='cliente')

#Ruta para obtener Clientes

@api_desubicados.get("/Clientes")
def get_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Clientes).all()
    return [
        {
            "id_cliente": c.id_cliente,
            "nombre": c.nombre,
            "primer_apellido": c.primer_apellido,
            "segundo_apellido": c.segundo_apellido,
            "fecha_nacimiento": c.fecha_nacimiento,
            "dni": c.dni,
            "calle": c.calle,
            "numero_casa": c.numero_casa,
            "localidad": c.localidad,
            "provincia": c.provincia,
            "cod_postal": c.cod_postal,
            "nacionalidad": c.nacionalidad,
            "puntos": c.puntos,
            "correo": c.correo,
            "contrasena": c.contrasena,
        }
        for c in clientes
    ]

#Ruta para obtener un cliente por correo
@api_desubicados.get("/Clientes/correo/")
def get_cliente_por_correo(correo: str = Query(...), db: Session = Depends(get_db)):
    cliente = db.query(Clientes).filter(Clientes.correo.like(correo)).first()
    
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

#BORRAR CLIENTES
@api_desubicados.delete("/Clientes/borrar/")
def delete_cliente(id_cliente: int, db: Session = Depends(get_db)):
    # Buscar el cliente por ID
    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Eliminar las relaciones con relojes si existen
    relaciones = db.query(Clientes_Relojes).filter(Clientes_Relojes.id_cliente == id_cliente).all()
    for relacion in relaciones:
        db.delete(relacion)

    # Eliminar el cliente
    db.delete(cliente)
    db.commit()

    return {"mensaje": "Cliente eliminado correctamente", "id_cliente": id_cliente}


# Modelo Pydantic para la creación de un cliente
class ClienteCreate(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: str
    dni: str
    calle: str
    numero_casa: str
    localidad: str
    provincia: str
    cod_postal: str
    nacionalidad: str
    puntos: int
    correo: str
    contrasena: str

#METODO CREA CLIENTES
@api_desubicados.post("/Clientes/crear")
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    try:
        # Convertir la fecha de nacimiento a formato correcto
        fecha_nacimiento = datetime.strptime(cliente.fecha_nacimiento, '%d-%m-%Y').strftime('%Y-%m-%d')

        nuevo_cliente = Clientes(
            nombre=cliente.nombre,
            primer_apellido=cliente.primer_apellido,
            segundo_apellido=cliente.segundo_apellido,
            fecha_nacimiento=fecha_nacimiento,  # Fecha en el formato correcto
            dni=cliente.dni,
            calle=cliente.calle,
            numero_casa=cliente.numero_casa,
            localidad=cliente.localidad,
            provincia=cliente.provincia,
            cod_postal=cliente.cod_postal,
            nacionalidad=cliente.nacionalidad,
            puntos=cliente.puntos,
            correo=cliente.correo,
            contrasena=cliente.contrasena,
        )

        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return {"mensaje": "Cliente creado correctamente", "id_trabajador": nuevo_cliente.id_cliente}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


#MODIFICAR CLIENTES
class ClientesUpdate(BaseModel):
    nombre: Optional[str]
    primer_apellido: Optional[str]
    segundo_apellido: Optional[str]
    fecha_nacimiento: Optional[str]  # Formato: 'dd-mm-YYYY'
    dni: Optional[str]
    calle: Optional[str]
    numero_casa: Optional[str]
    localidad: Optional[str]
    provincia: Optional[str]
    cod_postal: Optional[str]
    nacionalidad: Optional[str]
    correo: Optional[str]
    contrasena: Optional[str]

@api_desubicados.put("/Clientes/modificar/")
def update_cliente(id_cliente: int, datos: ClientesUpdate, db: Session = Depends(get_db)):
    # Primero buscamos al cliente en la base de datos.
    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()

    # Si no se encuentra el cliente, lanzamos un error 404.
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    try:
        # Iteramos sobre los campos que fueron modificados.
        for campo, valor in datos.dict(exclude_unset=True).items():
            # Si el campo es la fecha de nacimiento, la formateamos.
            if campo == "fecha_nacimiento":
                valor = datetime.strptime(valor, '%Y-%m-%d').strftime('%Y-%m-%d')
            setattr(cliente, campo, valor)

        # Hacemos commit de los cambios y refrescamos el cliente para que tenga los datos actualizados.
        db.commit()
        db.refresh(cliente)

        # Devolvemos un mensaje de éxito.
        return {"mensaje": "Cliente actualizado correctamente", "id_cliente": cliente.id_cliente}

    except Exception as e:
        # Si ocurre algún error, deshacemos el commit y mostramos el error.
        db.rollback()
        return {"error": str(e)}

 #AÑADIR PUNTOS CLIENTES
@api_desubicados.post("/Clientes/anadirPuntos/")
def anadir_puntos(id_cliente: int, puntos: int, db: Session = Depends(get_db)):
    if puntos <= 0:
        raise HTTPException(status_code=400, detail="El número de puntos a añadir debe ser mayor que 0")

    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente.puntos += puntos
    db.commit()
    db.refresh(cliente)

    return {
        "mensaje": f"Se añadieron {puntos} puntos al cliente.",
        "puntos_actuales": cliente.puntos
    }

#COBRAR PUNTOS CLIENTES
@api_desubicados.post("/Clientes/cobrarPuntos/")
def cobrar_puntos(id_cliente: int, puntos: int, db: Session = Depends(get_db)):
    if puntos <= 0:
        raise HTTPException(status_code=400, detail="El número de puntos a cobrar debe ser mayor que 0")

    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if cliente.puntos < puntos:
        raise HTTPException(status_code=400, detail="Puntos insuficientes para realizar el cobro")

    cliente.puntos -= puntos
    db.commit()
    db.refresh(cliente)

    return {
        "mensaje": f"Se cobraron {puntos} puntos al cliente.",
        "puntos_actuales": cliente.puntos
    }

       
#Modeloo SQAlcghemy para Relojes
class Relojes(Base):
    __tablename__ = 'Relojes'

    id_reloj = Column(String(17), primary_key=True)  
    ip = Column(String(45), nullable=True)  
    
    clientes = relationship('Clientes_Relojes', back_populates='reloj')
    
#Ruta para obtener Relojes
@api_desubicados.get("/Relojes")
def get_relojes(db: Session = Depends(get_db)):
    relojes = db.query(Relojes).all()
    return [
        {
            "id_reloj": c.id_reloj,
            "ip": c.ip,
        }
        for c in relojes
    ]


#Modelo SQAlcghemy para Clientes_Relojes
class Clientes_Relojes(Base):
    __tablename__ = 'Clientes_Relojes'

    id_cliente = Column(Integer, ForeignKey('Clientes.id_cliente'), primary_key=True)  # Clientes
    id_reloj = Column(String(17), ForeignKey('Relojes.id_reloj'), primary_key=True)  # Relojes
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)  # Fecha de asignación del reloj al cliente

    # Relaciones con las tablas Clientes y Relojes
    cliente = relationship('Clientes', back_populates='relojes')
    reloj = relationship('Relojes', back_populates='clientes')

@api_desubicados.get("/Clientes_Relojes")
def get_clientes_relojes(db: Session = Depends(get_db)):
    clientes_relojes = db.query(Clientes_Relojes).all()
    return [
        {
            "id_cliente": c.id_cliente,
            "id_reloj": c.id_reloj,
            "fecha_asignacion": c.fecha_asignacion,
        }
        for c in clientes_relojes
    ]

#Obtener cliente por mac del reloj

@api_desubicados.get("/Clientes_Relojes/obtenerPorMacReloj")
def obtener_cliente_por_mac_reloj(mac: str, db: Session = Depends(get_db)):
    asociacion = db.query(Clientes_Relojes).filter_by(id_reloj=mac).first()
    if not asociacion:
        raise HTTPException(status_code=404, detail="No se encontró una asociación para esa MAC")

    cliente = db.query(Clientes).filter_by(id_cliente=asociacion.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return cliente

# LO MAS NUEVO "EN PRUEBAS"
@api_desubicados.post("/Clientes_Relojes/asignar")
def asignar_reloj_cliente(id_cliente: int, id_reloj: str, db: Session = Depends(get_db)):
    # Verificar si el cliente existe
    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar si el reloj existe
    reloj = db.query(Relojes).filter(Relojes.id_reloj == id_reloj).first()
    if not reloj:
        raise HTTPException(status_code=404, detail="Reloj no encontrado")
    
    # Verificar si el reloj ya está asignado al cliente
    cliente_reloj = db.query(Clientes_Relojes).filter(Clientes_Relojes.id_cliente == id_cliente, Clientes_Relojes.id_reloj == id_reloj).first()
    if cliente_reloj:
        raise HTTPException(status_code=400, detail="El reloj ya está asignado a este cliente")
    
    # Asignar el reloj al cliente
    nuevo_cliente_reloj = Clientes_Relojes(id_cliente=id_cliente, id_reloj=id_reloj)
    db.add(nuevo_cliente_reloj)
    db.commit()
    db.refresh(nuevo_cliente_reloj)
    
    return {"mensaje": "Reloj asignado correctamente al cliente", "id_cliente": id_cliente, "id_reloj": id_reloj}

  
@api_desubicados.delete("/Clientes_Relojes/desasignar")
def desasignar_reloj_cliente(id_cliente: int, id_reloj: str, db: Session = Depends(get_db)):
    # Verificar si el cliente existe
    cliente = db.query(Clientes).filter(Clientes.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar si el reloj existe
    reloj = db.query(Relojes).filter(Relojes.id_reloj == id_reloj).first()
    if not reloj:
        raise HTTPException(status_code=404, detail="Reloj no encontrado")
    
    # Verificar si el reloj está asignado al cliente
    cliente_reloj = db.query(Clientes_Relojes).filter(Clientes_Relojes.id_cliente == id_cliente, Clientes_Relojes.id_reloj == id_reloj).first()
    if not cliente_reloj:
        raise HTTPException(status_code=400, detail="El reloj no está asignado a este cliente")
    
    # Eliminar la asignación
    db.delete(cliente_reloj)
    db.commit()
    
    return {"mensaje": "Reloj desasignado correctamente del cliente", "id_cliente": id_cliente, "id_reloj": id_reloj}


#RELOJ
@api_desubicados.get("/obtener_cliente_por_mac/{mac}")
def obtener_cliente_por_mac(mac: str, db: Session = Depends(get_db)):
    relacion = db.query(Clientes_Relojes).filter(Clientes_Relojes.id_reloj == mac).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Reloj no asignado a ningún cliente")
    
    cliente = db.query(Clientes).filter(Clientes.id_cliente == relacion.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return {
        "nombre": cliente.nombre,
        "puntos": cliente.puntos
    }

