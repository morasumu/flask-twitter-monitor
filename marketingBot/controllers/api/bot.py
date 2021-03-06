from flask import request, current_app, jsonify
from datetime import datetime
from sqlalchemy import or_

# from marketingBot.models import db
from marketingBot.models.Bot import db, Bot
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Notification import Notification
from marketingBot.controllers.api import api
from marketingBot.controllers.task_manager import start_bot_execution, stop_bot_execution
from marketingBot.controllers.cron import schedule_bot_running, remove_bot_from_schedule, modify_bot_schedule
from marketingBot.helpers.common import stringify, splitString2Array, json_parse
from marketingBot.helpers.wrapper import session_required

@api.route('/ping-bot', methods=['GET'])
def api_ping_bot():
  bot = db.session.query(Bot).filter_by(id=1).first()
  return jsonify({
    "status": True,
    "message": "pong",
    "data": bot.to_dict(),
  })

@api.route('/bots', methods=['GET'])
@session_required
def load_bots(self):
  skip = request.args.get('start')
  limit = request.args.get('length')
  # sortCol = request.args.get('order[0][column]')
  # sortDir = request.args.get('order[0][dir]')
  user_id = self.id
  # keyword = request.args.get('search[value]')

  bots = db.session.query(Bot).filter_by(user_id=user_id).limit(limit).offset(skip)
  app_keys = db.session.query(AppKey).filter_by(user_id=user_id).all()
  dict_keys = {}
  print('[App Keys]', app_keys)
  for app_key in app_keys:
    dict_keys[str(app_key.id)] = app_key.to_dict()
  print('[Keys]', dict_keys)
  data = []
  for idx, bot in enumerate(bots):
    bot = bot.format()
    bot_keys = []
    for key in bot.api_keys:
      key = str(key)
      if key in dict_keys:
        bot_keys.append(dict_keys[key])

    data.append([idx + 1, bot.name, bot.targets, bot_keys, bot.inclusion_keywords, bot.exclusion_keywords, bot.status, bot.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': 10,
    'iTotalDisplayRecords':10,
  })

# @deprecated. use 'create_bot_form' instead.
@api.route('/bots', methods=['POST'])
@session_required
def create_bot(self):
  payload = dict(request.get_json())
  
  bot = Bot(
    user_id = self.id,
    name = payload['name'],
    api_keys = payload['api_keys'] if payload['api_keys'] else '[]',
    targets = payload['targets'] if payload['targets'] else '[]',
    inclusion_keywords = payload['inclusion_keywords'] if payload['inclusion_keywords'] else '[]',
    exclusion_keywords = payload['exclusion_keywords'] if payload['exclusion_keywords'] else '[]',
    period = 1.0 if 'period' not in payload else payload['period'],
    status= payload['status'] if 'status' in payload else 'IDLE',
  )
  db.session.add(bot)
  db.session.commit()
  print('[Bot]', bot.to_dict(), bot.id)
  return jsonify({
    "status": True,
    "message": "A bot has been added!",
    "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
  })

# @deprecated. use 'update_bot_form' instead.
@api.route('/bots/<id>', methods=['PUT'])
@session_required
def update_bot_by_id(self, id):
  payload = dict(request.get_json())
  print('[Interval]', payload['interval'], payload['exclusion_keywords'])

  stop_bot_execution(id)

  bot = db.session.query(Bot).filter_by(id=id).first()
  bot.name = payload['name']
  bot.targets = payload['targets'] if 'targets' in payload else '[]'
  bot.api_keys = payload['api_keys'] if 'api_keys' in payload else '[]'
  bot.inclusion_keywords = payload['inclusion_keywords'] if 'inclusion_keywords' in payload else '[]'
  bot.exclusion_keywords = payload['exclusion_keywords'] if 'exclusion_keywords' in payload else '[]'
  bot.period = payload['interval'] if 'interval' in payload else 1.0


  db.session.commit()

  start_bot_execution(id)

  return jsonify({
    "status": True,
    "message": "A bot has been updated!",
    "upData": bot.to_dict(),
    "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
  })

@api.route('/bots/<id>', methods=['GET'])
@session_required
def get_bot_by_id(self, id):
  bot = db.session.query(Bot).filter_by(id=id).first()
  if not bot:
    return jsonify({
      "status": False,
      "message": "Bot does not exist!",
    })
  return jsonify({
    "status": True,
    "message": "success",
    "data": bot.to_dict(),
  })

@api.route('/bots/<bot_id>/sessions', methods=['GET'])
# @session_required
def get_sessions_of_bot(bot_id):
  # db.session.query(Notification.column1.distinct()).filter_by(column2 = 'some_column2_value').all();
  notifications = db.session.query(Notification).filter(Notification.bot_id == bot_id, or_(Notification.payload['type']=='SCHEDULE_RUN', Notification.payload['type']=="BOT_RUN")).all()
  print('[Notifications]', notifications)
  return jsonify({
    "status": True,
    "message": "success",
    "data": list(map(lambda noti: noti.to_dict(), notifications))
  })

@api.route('/bots/<id>', methods=['DELETE'])
@session_required
def delete_bot_by_id(self, id):
  bot = db.session.query(Bot).filter_by(id=id).one()
  if not bot:
    return jsonify({
      "status": False,
      "message": 'Bot does not exist!',
    })
  remove_bot_from_schedule(bot)
  db.session.delete(bot)
  db.session.commit()

  return jsonify({
    "status": True,
    "message": "Bot has been deleted!",
  })

@api.route('/bot_form', methods=['POST'])
@session_required
def create_bot_form(self):
  try:
    payload = dict(request.form)
    str_targets = request.files.get('targets').read().decode('utf-8') if 'targets' in request.files else payload['targets']
    str_in_keywords = request.files.get('inclusion_keywords').read().decode('utf-8') if 'inclusion_keywords' in request.files else payload['inclusion_keywords']
    str_ex_keywords = request.files.get('exclusion_keywords').read().decode('utf-8') if 'exclusion_keywords' in request.files else payload['exclusion_keywords']

    bot = Bot(
      user_id = self.id,
      name = payload['name'],
      type = payload['type'],
      targets = (splitString2Array(str_targets)),
      api_keys = (splitString2Array(payload['api_keys'])),
      inclusion_keywords = (splitString2Array(str_in_keywords)),
      exclusion_keywords = (splitString2Array(str_ex_keywords)),
      period = payload['interval'] if 'interval' in payload else 1.0,
      start_time = payload['start_time'],
      end_time = payload['end_time'],
      schedule_interval = payload['schedule_interval'],
      schedule_time = payload['schedule_time'],
      metrics = json_parse(payload['metrics']),
      rank_factors = json_parse(payload['rank_factors']),
      status= payload['status'] if 'status' in payload else 'IDLE',
      enable_translation = True if payload['enable_translation'] == 'true' else False,
      target_langs = json_parse(payload['target_langs']),
      translator = payload['translator'],
      enable_cutout = True if payload['enable_cutout'] == 'true' else False,
      cutout = int(payload['cutout']),
      enable_automation = True if payload['enable_automation'] == 'true' else False,
      auto_action = payload['auto_action'],
      default_text = payload['default_text'],
    )

    db.session.add(bot)
    db.session.commit()
    bot_obj = bot.to_dict()
    db.session.expire(bot)

    schedule_bot_running(bot = bot_obj)
    return jsonify({
      "status": True,
      "message": "A bot has been added!",
      "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
    })
  except Exception as e:
    return jsonify({
      "status": False,
      "message": 'Failed to add a bot',
    })

@api.route('/bot_form/<id>', methods=['PUT'])
@session_required
def update_bot_form(self, id):
  payload = dict(request.form)
  str_targets = request.files.get('targets').read().decode('utf-8') if 'targets' in request.files else payload['targets']
  str_in_keywords = request.files.get('inclusion_keywords').read().decode('utf-8') if 'inclusion_keywords' in request.files else payload['inclusion_keywords']
  str_ex_keywords = request.files.get('exclusion_keywords').read().decode('utf-8') if 'exclusion_keywords' in request.files else payload['exclusion_keywords']

  bot = db.session.query(Bot).filter_by(id=id).first()
  bot.name = payload['name']
  bot.type = payload['type']
  bot.targets = (splitString2Array(str_targets))
  bot.api_keys = (splitString2Array(payload['api_keys']))
  bot.inclusion_keywords = (splitString2Array(str_in_keywords))
  bot.exclusion_keywords = (splitString2Array(str_ex_keywords))
  bot.period = payload['interval'] if 'interval' in payload else 1.0
  bot.start_time = payload['start_time']
  bot.end_time = payload['end_time']
  bot.schedule_interval = payload['schedule_interval']
  bot.schedule_time = payload['schedule_time']
  bot.enable_translation = True if payload['enable_translation'] == 'true' else False
  bot.target_langs = json_parse(payload['target_langs'])
  bot.translator = payload['translator']
  print('[Metrics]', payload['metrics'])
  bot.metrics = json_parse(payload['metrics'])
  bot.rank_factors = json_parse(payload['rank_factors'])
  bot.enable_cutout = True if payload['enable_cutout'] == 'true' else False
  bot.cutout = int(payload['cutout'])
  bot.enable_automation = True if payload['enable_automation'] == 'true' else False
  bot.auto_action = payload['auto_action']
  bot.default_text = payload['default_text']

  bot_obj = bot.to_dict()
  db.session.commit()
  modify_bot_schedule(bot = bot_obj)
  # start_bot_execution(id)

  return jsonify({
    "status": True,
    "message": "A bot has been updated!",
    "upData": bot.to_dict(),
    "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
  })
