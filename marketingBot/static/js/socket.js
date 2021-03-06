const EVENT = {
  NEW_TWEET_FOUND: 'NEW_TWEET_FOUND',
  BOT_MANUAL_START: 'BOT_MANUAL_START',
  BOT_SCHEDULE_START: 'BOT_SCHEDULE_START',
  BOT_FINISHED: 'BOT_FINISHED',
  BOT_STOPPED: 'BOT_STOPPED',
};



var socket = io.connect('/');

socket.on( 'connect', function() {
  console.log('[SocketID]', socket.id)

  // socket.emit( 'PING', {
  //   user_name : 'Aleks',
  //   message : 'Hello Flask Socket'
  // })
})

// socket.on('PONG', args => {
//   console.log('[EVENT][PONG]', args)
// })

socket.on(EVENT.NEW_TWEET_FOUND, args => {
  console.log('[New Tweet]', args);
  toastr.info(args.translated, `${args.bot} - New tweet from @${args.user_name}`)
});

socket.on(EVENT.BOT_MANUAL_START, args => {
  toastr.info(args.message, 'Bot Status');
  if (typeof refreshTable === 'function') {
    refreshTable();
  }
});

socket.on(EVENT.BOT_SCHEDULE_START, args => {
  toastr.info(args.message, 'Bot Status');
  if (typeof refreshTable === 'function') {
    refreshTable();
  }
});

socket.on(EVENT.BOT_FINISHED, args => {
  toastr.info(args.message, 'Bot Status');
  if (typeof refreshTable === 'function') {
    refreshTable();
  }
});

socket.on(EVENT.BOT_STOPPED, args => {
  toastr.info(args.message, 'Bot Status');
  if (typeof refreshTable === 'function') {
    refreshTable();
  }
});
