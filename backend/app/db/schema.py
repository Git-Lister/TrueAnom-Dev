from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    kind = Column(String, nullable=False)
    url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    documents = relationship("Document", back_populates="source")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    external_id = Column(String, index=True)
    doc_type = Column(String, index=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    event_time_start = Column(DateTime, nullable=True)
    event_time_end = Column(DateTime, nullable=True)
    ingest_time = Column(DateTime, nullable=True)
    text = Column(Text, nullable=True)
    raw_path = Column(String, nullable=True)
    ocr_confidence = Column(Integer, nullable=True)
    is_searchable = Column(Boolean, default=True)
    meta_json = Column(JSON, nullable=True)

    source = relationship("Source", back_populates="documents")
    pages = relationship("Page", back_populates="document")
    mentions = relationship("EntityMention", back_populates="document")
    relationships = relationship("Relationship", back_populates="source_document")


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    bates_id = Column(String, nullable=True, index=True)

    document = relationship("Document", back_populates="pages")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    canonical_name = Column(String, index=True)
    display_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    aliases = Column(JSON, nullable=True)
    external_links = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=True)

    mentions = relationship("EntityMention", back_populates="entity")
    relationships_from = relationship(
        "Relationship",
        back_populates="from_entity",
        foreign_keys="Relationship.from_entity_id",
    )
    relationships_to = relationship(
        "Relationship",
        back_populates="to_entity",
        foreign_keys="Relationship.to_entity_id",
    )


class EntityMention(Base):
    __tablename__ = "entity_mentions"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=True)
    span_start = Column(Integer, nullable=True)
    span_end = Column(Integer, nullable=True)
    mention_text = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)
    event_time = Column(DateTime, nullable=True)

    entity = relationship("Entity", back_populates="mentions")
    document = relationship("Document", back_populates="mentions")
    page = relationship("Page")


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    relationship_type = Column(String, index=True)
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    from_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    to_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    event_time = Column(DateTime, nullable=True)
    weight = Column(Integer, nullable=True)
    meta_json = Column(JSON, nullable=True)

    source_document = relationship("Document", back_populates="relationships")
    from_entity = relationship(
        "Entity",
        foreign_keys=[from_entity_id],
        back_populates="relationships_from",
    )
    to_entity = relationship(
        "Entity",
        foreign_keys=[to_entity_id],
        back_populates="relationships_to",
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    event_type = Column(String, index=True)  # e.g. "email", "flight", "meeting"
    event_time = Column(DateTime, index=True)
    description = Column(Text, nullable=True)
    meta_json = Column(JSON, nullable=True)

    document = relationship("Document")
