var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  return res.render('pages/index');
});


/* GET about page. */ 
router.get('/about', function(req, res, next) {
  return res.render('pages/about');
});


/* GET live page */
router.get('/live', function(req, res, next) {
  return res.render('pages/live');
});


/* GET historic page */
router.get('/historic', function(req, res, next) {
  return res.render('pages/historic');
});


module.exports = router;
