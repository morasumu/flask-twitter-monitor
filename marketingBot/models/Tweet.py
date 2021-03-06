from datetime import datetime
from marketingBot import db

class Tweet(db.Model):
  __tablename__ = 'tweets'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable = False)
  bot_id = db.Column(db.Integer, nullable = False)
  session = db.Column(db.Integer, nullable = False)
  target = db.Column(db.String(50), nullable=False)
  text = db.Column(db.String(500), nullable=False)
  entities = db.Column(db.JSON)
  translated = db.Column(db.String(600), nullable=False)
  tweeted = db.Column(db.SmallInteger, default=0)
  metrics = db.Column(db.JSON)
  rank_index = db.Column(db.Numeric(15, 8))
  media = db.Column(db.JSON)

  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, bot_id, session, target, text, translated, entities, metrics = {}, rank_index = 0, media = [], tweeted = False, **args):
    self.user_id = user_id
    self.bot_id = bot_id
    self.session = session
    self.target = target
    self.text = text
    self.entities = entities
    self.translated = translated
    self.tweeted = tweeted
    self.metrics = metrics
    self.rank_index = rank_index
    self.media = media

    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()

  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      bot_id = self.bot_id,
      session = self.session,
      target = self.target,
      text = self.text,
      translated = self.translated,
      entities = self.entities,
      tweeted = self.tweeted,
      metrics = self.metrics,
      rank_index = str(self.rank_index),
      media = self.media,
      created_at=self.created_at,
      updated_at=self.updated_at
    )

 