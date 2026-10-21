const port = 32000;
const ip = '0.0.0.0';
const express = require('express');
const app = express();
app.use(express.static('dist'));
app.listen(port, ip, () => console.log(`Listening on port ${port}`));
