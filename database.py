from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# -----------------------------
# Database Configuration
# -----------------------------
engine = create_engine("sqlite:///inventory.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------------
# Models
# -----------------------------
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Active / Inactive

    assets = relationship("Asset", back_populates="vendor")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    status = Column(String, nullable=False)

    assets = relationship("Asset", back_populates="location")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Active / Retired / Disposed

    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    vendor = relationship("Vendor", back_populates="assets")
    location = relationship("Location", back_populates="assets")


# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()

    # Prevent duplicate seeding
    if session.query(Vendor).first():
        session.close()
        return

    # Vendors
    vendor1 = Vendor(name="Dell", status="Active")
    vendor2 = Vendor(name="HP", status="Inactive")

    # Locations
    location1 = Location(name="Warehouse A", city="Cairo", status="Active")
    location2 = Location(name="Warehouse B", city="Alex", status="Active")

    # Assets
    asset1 = Asset(
        name="Laptop 1",
        category="Laptop",
        status="Active",
        vendor=vendor1,
        location=location1
    )

    asset2 = Asset(
        name="Printer 1",
        category="Printer",
        status="Retired",
        vendor=vendor2,
        location=location2
    )

    session.add_all([
        vendor1, vendor2,
        location1, location2,
        asset1, asset2
    ])

    session.commit()
    session.close()