from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Laptop


Base.metadata.create_all(bind=engine)


def cargar_laptops_iniciales():
    db = SessionLocal()

    try:
        if db.query(Laptop).count() == 0:
            laptops = [
                Laptop(
                    marca="Dell",
                    modelo="Latitude 5440",
                    ram_gb=16,
                    disponible=True
                ),
                Laptop(
                    marca="Lenovo",
                    modelo="ThinkPad E14",
                    ram_gb=8,
                    disponible=False
                ),
                Laptop(
                    marca="HP",
                    modelo="ProBook 450",
                    ram_gb=16,
                    disponible=True
                )
            ]

            db.add_all(laptops)
            db.commit()

    finally:
        db.close()


cargar_laptops_iniciales()


app = FastAPI(
    title="API del laboratorio de cómputo"
)


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


def laptop_a_dict(laptop: Laptop):
    return {
        "id": laptop.id,
        "marca": laptop.marca,
        "modelo": laptop.modelo,
        "ram_gb": laptop.ram_gb,
        "disponible": laptop.disponible
    }


@app.get("/")
def inicio():
    return {
        "mensaje": "API del laboratorio de cómputo"
    }


@app.get("/laptops")
def listar_laptops(
    db: Session = Depends(get_db)
):
    laptops = (
        db.query(Laptop)
        .order_by(Laptop.id)
        .all()
    )

    return [
        laptop_a_dict(laptop)
        for laptop in laptops
    ]


@app.get("/laptops/disponibles")
def listar_laptops_disponibles(
    db: Session = Depends(get_db)
):
    laptops = (
        db.query(Laptop)
        .filter(Laptop.disponible.is_(True))
        .order_by(Laptop.id)
        .all()
    )

    return [
        laptop_a_dict(laptop)
        for laptop in laptops
    ]


@app.get("/laptops/{laptop_id}")
def obtener_laptop(
    laptop_id: int,
    db: Session = Depends(get_db)
):
    laptop = (
        db.query(Laptop)
        .filter(Laptop.id == laptop_id)
        .first()
    )

    if laptop is None:
        raise HTTPException(
            status_code=404,
            detail="Laptop no encontrada"
        )

    return laptop_a_dict(laptop)


@app.post("/laptops", status_code=201)
def crear_laptop(
    datos: LaptopCreate,
    db: Session = Depends(get_db)
):
    nueva_laptop = Laptop(
        marca=datos.marca,
        modelo=datos.modelo,
        ram_gb=datos.ram_gb,
        disponible=True
    )

    db.add(nueva_laptop)
    db.commit()
    db.refresh(nueva_laptop)

    return laptop_a_dict(nueva_laptop)
