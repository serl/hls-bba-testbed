var express = require('express');
var app = express();
var morgan = require('morgan');
var path = require('path');

app.set('port', (process.env.PORT || 3000));

function timestamp() {
  return (new Date()).getTime()/1000;
}

morgan.token('timestamp', function(req, res) { return timestamp(); });
app.use(morgan(':timestamp :method :url :status :res[content-length] - :response-time ms'));

app.use('/static', express.static(path.join(__dirname, 'static')));

app.get('/', function (req, res) {
  res.send('wat?\n');
});


var server;
function startHTTPServer() {
  server = app.listen(app.get('port'), function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('%s LISTENING at http://%s:%s', timestamp(), host, port);
  });
}
startHTTPServer();
