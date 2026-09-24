from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


project_technology = Table(
    "project_technology",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("technology_id", ForeignKey("technologies.id"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    bio: Mapped[str] = mapped_column(String(500), default="")
    github_url: Mapped[str] = mapped_column(String(300))
    projects: Mapped[list["Project"]] = relationship(back_populates="profile")


class Technology(Base):
    __tablename__ = "technologies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    projects: Mapped[list["Project"]] = relationship(secondary=project_technology, back_populates="technologies")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(1000))
    repository_url: Mapped[str] = mapped_column(String(300))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    profile: Mapped[Profile] = relationship(back_populates="projects")
    technologies: Mapped[list[Technology]] = relationship(secondary=project_technology, back_populates="projects")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="project")


class Feedback(Base):
    __tablename__ = "feedbacks"
    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(120))
    comment: Mapped[str] = mapped_column(String(1000))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped[Project] = relationship(back_populates="feedbacks")


class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    bio: str = Field(default="", max_length=500)
    github_url: HttpUrl


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    bio: str
    github_url: str


class TechnologyIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TechnologyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProjectIn(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=1000)
    repository_url: HttpUrl
    profile_id: int = Field(gt=0)
    technology_ids: list[int] = Field(default_factory=list)


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    repository_url: str
    profile_id: int
    technology_ids: list[int]


engine = create_engine("sqlite:///./devshowcase.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="DevShowcase API", lifespan=lifespan)


def get_db():
    with SessionLocal() as db:
        yield db


Db = Annotated[Session, Depends(get_db)]


@app.post("/api/profiles", response_model=ProfileOut, status_code=201)
def create_profile(data: ProfileIn, db: Db):
    profile = Profile(name=data.name, bio=data.bio, github_url=str(data.github_url))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/api/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Db):
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(404, "Perfil não encontrado")
    return profile


@app.post("/api/technologies", response_model=TechnologyOut, status_code=201)
def create_technology(data: TechnologyIn, db: Db):
    if db.scalar(select(Technology).where(Technology.name == data.name)):
        raise HTTPException(409, "Tecnologia já cadastrada")
    technology = Technology(name=data.name)
    db.add(technology)
    db.commit()
    db.refresh(technology)
    return technology


@app.get("/api/technologies", response_model=list[TechnologyOut])
def list_technologies(db: Db):
    return db.scalars(select(Technology).order_by(Technology.id)).all()


@app.post("/api/projects", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectIn, db: Db):
    if db.get(Profile, data.profile_id) is None:
        raise HTTPException(404, "Perfil não encontrado")
    ids = set(data.technology_ids)
    technologies = db.scalars(select(Technology).where(Technology.id.in_(ids))).all() if ids else []
    if len(technologies) != len(ids):
        raise HTTPException(404, "Uma ou mais tecnologias não foram encontradas")
    project = Project(title=data.title, description=data.description,
                      repository_url=str(data.repository_url), profile_id=data.profile_id,
                      technologies=technologies)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_response(project)


def project_response(project: Project) -> ProjectOut:
    return ProjectOut(id=project.id, title=project.title, description=project.description,
                      repository_url=project.repository_url, profile_id=project.profile_id,
                      technology_ids=[tech.id for tech in project.technologies])


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects(db: Db):
    return [project_response(project) for project in db.scalars(select(Project).order_by(Project.id)).all()]
