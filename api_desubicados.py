from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy import Date, DateTime
from datetime import datetime


# Configuración de la base de datos de DesUbicados
SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://diego:diego123@localhost/desubicados"

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la clase base para los modelos
Base = declarative_base()

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


#Modeloo SQAlcghemy para Relojes
class Relojes(Base):
    __tablename__ = 'Relojes'

    id_reloj = Column(String(17), primary_key=True)  
    ip = Column(String(45), nullable=True)  
    
    clientes = relationship('Clientes_Relojes', back_populates='reloj')


#Modelo SQAlcghemy para Clientes_Relojes
class Clientes_Relojes(Base):
    __tablename__ = 'Clientes_Relojes'

    id_cliente = Column(Integer, ForeignKey('Clientes.id_cliente'), primary_key=True)  # Clientes
    id_reloj = Column(String(17), ForeignKey('Relojes.id_reloj'), primary_key=True)  # Relojes
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)  # Fecha de asignación del reloj al cliente

    # Relaciones con las tablas Clientes y Relojes
    cliente = relationship('Clientes', back_populates='relojes')
    reloj = relationship('Relojes', back_populates='clientes')
    
# Dependencia para obtennr la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear el router de esta API
api_desubicados = APIRouter()

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
            "puesto": t.puesto,
        }
        for t in trabajadores
    ]


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
        }
        for c in clientes
    ]

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
