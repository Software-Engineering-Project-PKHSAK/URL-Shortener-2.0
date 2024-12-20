#MIT License
#
#Copyright (c) 2024 Akarsh Reddy, Himanshu Singh and Prateek Kamath
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import uuid
try:
	from ..extensions import db
except ImportError:
	from extensions import db
from sqlalchemy.dialects.postgresql import UUID

class Engagements(db.Model):
    __tablename__ = 'engagements'
 
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
		
    utm_source = db.Column(db.String(100), nullable=True)
    utm_medium = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    utm_term = db.Column(db.String(100), nullable=True)
    utm_content = db.Column(db.String(100), nullable=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False, server_onupdate=db.func.now())
    # make a relationship with 'Link' model
    link_id = db.Column(UUID(as_uuid=True), db.ForeignKey('links.id', ondelete="CASCADE"))
    long_url = db.Column(db.String(100), nullable=True)
    device_os = db.Column(db.String(100), nullable=True)
    device_browser = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(100), nullable=True)

    def to_json(self):
        return {
        'id': self.id,
        'link_id':self.link_id,
        'utm_source':self.utm_source,
        'utm_medium':self.utm_medium,
        'utm_campaign':self.utm_campaign,
        'utm_term':self.utm_term,
        'utm_content':self.utm_content,
        'long_url': self.long_url,
        'created_on':self.created_on, 
        'updated_on':self.updated_on,
        'device_type': self.device_type,
        'device_os': self.device_os,
        'device_browser': self.device_browser
        }

    def __repr__(self):
        return '<id {}>'.format(self.id)

def load_engagements(id):
    return Engagements.query.get(id)
