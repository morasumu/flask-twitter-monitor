from flask import render_template, jsonify, request
from sqlalchemy.sql import text

from marketingBot import db, app
from marketingBot.controllers.cron import get_next_run_time
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Bot import Bot
from marketingBot.models.Notification import Notification
from marketingBot.models.Tweet import Tweet
from marketingBot.helpers.common import timestamp
from marketingBot.helpers.wrapper import session_required

@app.context_processor
def my_utility_processor():
  def time_now():
    return timestamp()
  def current_route():
    return request.url_rule.rule
  
  return dict(timestamp=time_now, current_route = current_route)

@app.route('/ping')
def ping():
  print('[Ping] requested')
  return jsonify({ "status": True, "message": "Pong" })

@app.route('/dashboard', methods=['GET'])
@session_required
def dashboard(self):
  apps = db.session.query(AppKey).filter_by(user_id = self.id).count()
  bots = db.session.query(Bot).filter_by(user_id = self.id).count()
  tweets = db.session.query(Tweet).filter_by(user_id = self.id).count()
  notifications = db.session.query(Notification).filter_by(user_id = self.id).count()
  data = {
    "apps": apps,
    "bots": bots,
    "tweets": tweets,
    "notifications": notifications,
  }
  return render_template('panel/dashboard.html', data = data)

@app.route('/api-apps')
@session_required
def api_apps(self):
  return render_template('panel/api-apps.html')


@app.route('/load-api-apps')
@session_required
def load_api_apps(self):
  skip = request.args.get('start')
  limit = request.args.get('length')
  sortCol = request.args.get('order[0][column]')
  sortDir = request.args.get('order[0][dir]')
  user_id = self.id
  keyword = request.args.get('search[value]')

  apps = db.session.query(AppKey).filter_by(user_id=user_id).limit(limit).offset(skip)
  
  data = []
  for idx, app in enumerate(apps):
    data.append([idx + 1, app.name, f"{app.consumer_key}:{app.consumer_secret}:{app.access_token}:{app.access_token_secret}:{app.bearer_token}", app.valid, app.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': 10,
    'iTotalDisplayRecords':10,
  })


# Add a new API app.
@app.route('/api-app', methods=['POST'])
@session_required
def add_api_app(self):
  payload = request.get_json()
  print('[Payload]', payload)
  isExist = db.session.query(AppKey).filter_by(consumer_key=payload['consumer_key'], consumer_secret=payload['consumer_secret']).first()
  if (isExist):
    # flash('This API app already exists!')
    # return render_template('panel/api-apps.html')
    return jsonify({
      "status": False,
      "message": "This API app already exists!",
    })
  print('[Active]', payload['valid'])
  appKey = AppKey(
    user_id = self.id,
    consumer_key = payload['consumer_key'],
    consumer_secret = payload['consumer_secret'],
    access_token = payload['access_token'],
    access_token_secret = payload['access_token_secret'],
    bearer_token = payload['bearer_token'],
    name = payload['name'],
    valid = payload['valid'],
  )
  db.session.add(appKey)
  db.session.commit()
  # return render_template('panel/api-apps.html')
  return jsonify({
    "status": True,
    "message": "Data has been added!",
  })


@app.route('/bots', methods=['GET'])
@session_required
def bots_page(self):
  api_keys = db.session.query(AppKey).filter_by(user_id=self.id,valid=True).all()
  apps = []
  for api_key in api_keys:
    apps.append(api_key.to_dict())
  data = {
    "time": timestamp(),
    "api_apps": apps,
    "names": ['A', 'B']
  }
  return render_template('panel/bots.html', data=data)


@app.route('/load-bots', methods=['GET', 'POST'])
@session_required
def load_bots_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  user_id = self.id

  columns = ['bots.id', 'name', 'type', 'targets', '', 'api_keys', '', '', 'enable_cutout', 'cutout', 'status']
  order_by = text(f"{columns[int(sortCol)]} {sortDir}")

  print('[Sort]', sortCol, sortDir)
  bots = db.session.query(Bot).filter_by(user_id=user_id).order_by(order_by).limit(limit).offset(skip)
  total = db.session.query(Bot).filter_by(user_id = user_id).count()
  app_keys = db.session.query(AppKey).filter_by(user_id=user_id).all()
  dict_keys = {}

  for app_key in app_keys:
    dict_keys[str(app_key.id)] = app_key.to_dict()

  data = []
  for idx, bot in enumerate(bots):
    bot = bot.format()
    bot_keys = []
    for key in bot.api_keys:
      key = str(key)
      if key in dict_keys:
        bot_keys.append(dict_keys[key])

    data.append([
      idx + 1, bot.name,
      {
        'type': bot.type,
        'next_time': get_next_run_time(bot.id),
      },
      bot.targets,
      [float(bot.period), bot.start_time, bot.end_time], bot_keys,
      bot.inclusion_keywords, bot.exclusion_keywords,
      bot.enable_cutout, bot.cutout,
      bot.status, bot.id,      
    ])

  return jsonify({
    'data': data,
    'draw': payload['draw'],
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })


# 
# Tweet Page
@app.route('/tweets', methods=['GET'])
@session_required
def tweets_page(self):
  bots = db.session.query(Bot).filter_by(user_id=self.id).all()
  bots_dict = []
  for bot in bots:
    bots_dict.append(bot.to_dict())
  data = {
    "bots": bots_dict,
  }
  return render_template('panel/tweets.html', data = data)

@app.route('/load-tweets', methods=['GET', 'POST'])
@session_required
def load_tweets_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  keyword = payload['keyword']
  bot_id = int(payload['bot'])
  session_id = int(payload['session'])
  print('session_id', session_id)
  columns = ['tweets.id', 'bot_name', 'session_time', 'target', 'tweets.text', 'translated',
    "JSON_EXTRACT(tweets.metrics, '$.followers')",
    "JSON_EXTRACT(tweets.metrics, '$.friends')",
    "JSON_EXTRACT(tweets.metrics, '$.statuses')",
    "JSON_EXTRACT(tweets.metrics, '$.listed')",
    "JSON_EXTRACT(tweets.metrics, '$.tweet.retweets')",
    "JSON_EXTRACT(tweets.metrics, '$.tweet.favorite')",
    'rank_index',
    'tweeted', 'tweets.created_at']

  user_id = self.id
  # keyword = request.args.get('search[value]')
  # tweets = Tweet.query.filter_by(user_id = user_id).limit(limit).offset(skip)
  order_by = text(f"{columns[int(sortCol)]} {sortDir}")
  tweets = db.session.query(
      Tweet#, Bot
    # ).filter(Tweet.bot_id == Bot.id
    ).join(Bot, Bot.id == Tweet.bot_id, isouter = True
    ).join(Notification, Notification.id == Tweet.session, isouter = True
    ).filter(Tweet.user_id == user_id)
  if keyword:
    tweets = tweets.filter(Tweet.text.like(f"%{keyword}%"))
  if bot_id > 0:
    tweets = tweets.filter(Tweet.bot_id == bot_id)
  if session_id > 0:
    tweets = tweets.filter(Tweet.session == session_id)
  tweets =  tweets.with_entities(Tweet.id, Tweet.bot_id, Tweet.target, Tweet.text, Tweet.translated, Tweet.tweeted, Tweet.entities, Tweet.created_at, Tweet.metrics, Tweet.rank_index, Bot.name.label('bot_name'), Notification.created_at.label('session_time')
    ).order_by(order_by).limit(limit).offset(skip)

  # total = Tweet.query.filter_by(user_id = user_id).count()
  # total = db.session.query(Tweet, Bot).filter(Bot.id == Tweet.bot_id)
  total = db.session.query(Tweet).join(Bot, Bot.id == Tweet.bot_id, isouter = True)

  if keyword:
    total = total.filter(Tweet.text.like(f"%{keyword}%"))
  if bot_id > 0:
    total = total.filter(Tweet.bot_id == bot_id)
  if session_id > 0:
    total = total.filter(Tweet.session == session_id)
  total = total.count()

  bots = db.session.query(Bot).filter_by(user_id = user_id).all()
  dict_bots = {}
  for bot in bots:
    dict_bots[str(bot.id)] = bot.to_dict()
  
  data = []
  for idx, tweet in enumerate(tweets):
    data.append([
      idx + 1,
      tweet.bot_name,
      tweet.session_time,
      tweet.target,
      tweet.text,
      tweet.translated,
      tweet.metrics['followers'] if 'followers' in tweet.metrics else 0,
      tweet.metrics['friends'] if 'friends' in tweet.metrics else 0,
      tweet.metrics['statuses'] if 'statuses' in tweet.metrics else 0,
      tweet.metrics['listed'] if 'listed' in tweet.metrics else 0,
      tweet.metrics['tweet']['retweets'] if 'tweet' in tweet.metrics else 0,
      tweet.metrics['tweet']['favorite'] if 'tweet' in tweet.metrics else 0,
      str(tweet.rank_index),
      tweet.tweeted,
      tweet.created_at,
      { "id": tweet.id, "tweet_id": tweet.entities['id_str'] },
    ])
  return jsonify({
    'data': data,
    'draw': payload['draw'],
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })

#
# Notification Page
@app.route('/notifications', methods=['GET'])
@session_required
def notification_page(self):
  return render_template('panel/notifications.html')


@app.route('/load-notifications', methods=['GET', 'POST'])
@session_required
def load_notifications_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  columns = ['notifications.id', 'bot_name', 'notifications.text',
    "JSON_EXTRACT(notifications.payload, '$.type')",
    'notifications.created_at']

  user_id = self.id

  order_by = text(f"{columns[int(sortCol)]} {sortDir}")
  notifications = db.session.query(
      Bot, Notification
    ).filter(Bot.id == Notification.bot_id
    ).filter(Notification.user_id == user_id
    ).with_entities(Notification.id, Notification.user_id, Notification.bot_id, Notification.text, Notification.payload, Notification.created_at, Bot.name.label('bot_name')
    ).order_by(order_by).limit(limit).offset(skip)

  # total = Notification.query.filter_by(user_id = user_id).count()
  total = db.session.query(Bot, Notification).filter(Bot.id == Notification.bot_id).count()

  data = []
  for idx, notification in enumerate(notifications):
    data.append([
      idx + 1,
      notification.bot_name,
      notification.text,
      notification.payload,
      notification.created_at,
      { "id": notification.id },
    ])
  return jsonify({
    'data': data,
    'draw': payload['draw'],
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })
