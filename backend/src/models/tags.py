import uuid
try:
	from ..extensions import db
except ImportError:
	from extensions import db
from sqlalchemy.dialects.postgresql import UUID

# Tag model to represent individual tags
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Establish many-to-many relationship with Link
    links = db.relationship('Link', secondary='link_tags', back_populates='tags')

    def __repr__(self):
        return f"<Tag {self.name}>"


# Association table to handle many-to-many relationship between Link and Tag
class LinkTags(db.Model):
    __tablename__ = 'link_tags'

    link_id = db.Column(UUID(as_uuid=True), db.ForeignKey('links.id'), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tags.id'), primary_key=True)
