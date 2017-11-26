const path = require('path');
const config = require(path.join(__dirname,'server.json'));
const express = require('express');
const app = express();

app.use('/rrd_images', express.static('output'));

app.get('/', (req, res) => res.send('Hello World!'));


const port = config.server.port;
app.listen(port, () => console.log(`Server is listening on port ${port}!`))
