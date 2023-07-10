from typing import Optional

from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SimRel2(Base):
    """Declarative ORM example"""

    __tablename__ = "sim_file2"

    id: Mapped[int] = mapped_column(primary_key=True)
    feature1: Mapped[Optional[int]]
    feature2: Mapped[Optional[int]]
    feature3: Mapped[Optional[int]]
    feature4: Mapped[Optional[int]]
    feature5: Mapped[Optional[float]]
    feature6: Mapped[Optional[float]]
    feature7: Mapped[Optional[int]]
    feature8: Mapped[Optional[int]]
    feature9: Mapped[Optional[int]]


def create_table(table_name: str, feature_column_names: list[str], feature_column_type=Integer) -> Table:
    """Programmatically creates table schemas"""
    return Table(
        table_name,
        Base.metadata,
        Column("id", Integer, primary_key=True),
        *[Column(name, feature_column_type, nullable=True) for name in feature_column_names],
    )


class SimRel1(Base):
    __table__ = create_table("sim_file1", [f"feature{i}" for i in range(1, 30)])


class SimRel3(Base):
    __table__ = create_table("sim_file3", [f"feature{i}" for i in range(1, 26)])
