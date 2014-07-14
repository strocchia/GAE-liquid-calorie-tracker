import cgi
import datetime
import time
import os
import urllib
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template

class LiquidIntake(ndb.Model):
  indexer = ndb.IntegerProperty()
  author = ndb.StringProperty()
  liqOrCal = ndb.StringProperty()
  content = ndb.StringProperty()
  content_diff = ndb.StringProperty()
  date_automatic = ndb.DateTimeProperty(auto_now_add=True)
  date_entered = ndb.StringProperty()

  @classmethod
  def query_liquid(cls, ancestor_key):
    return cls.query(ancestor=ancestor_key).order(-cls.date_automatic)

class CaloricIntake(ndb.Model):
  indexer = ndb.IntegerProperty()
  author = ndb.StringProperty()
  liqOrCal = ndb.StringProperty()
  author = ndb.StringProperty()
  content = ndb.StringProperty()
  content_diff = ndb.StringProperty()
  date_automatic = ndb.DateTimeProperty(auto_now_add=True)
  date_entered = ndb.StringProperty()

  @classmethod
  def query_calorie(cls, ancestor_key):
    return cls.query(ancestor=ancestor_key).order(-cls.date_automatic)

class MainPage(webapp2.RequestHandler):
  def get(self):
    
    numEntriesToFetch = 10

    user_name = self.request.get('user_name')

    whichtracker = self.request.get('liquidOrCaloriesHiddenInput')

    ''' we set the "LiquidsDrank" entity to be the parent of another entity without explicitly creating it '''
    ancestor_key_liquid = ndb.Key("LiquidsDrank", user_name or "*notitle*")
    ancestor_key_calorie = ndb.Key("CaloriesEaten", user_name or "*notitle*")

    liquids = LiquidIntake.query_liquid(ancestor_key_liquid).fetch(numEntriesToFetch)
    calories = CaloricIntake.query_calorie(ancestor_key_calorie).fetch(numEntriesToFetch)

    counter_liquid = 0
    counter_calorie = 0
    i_count_liquid = numEntriesToFetch
    i_count_calorie = numEntriesToFetch
    prevOrFirst = "first"
    toGraph = 0

    for liquid in liquids:

      i_count_liquid = i_count_liquid - 1
      counter_liquid = counter_liquid + 1

    for calorie in calories:
      i_count_calorie = i_count_calorie - 1
      counter_calorie = counter_calorie + 1

    if counter_liquid == 0:
      prevOrFirst_liquid = "first"
      toGraph_liquid = 0
    if counter_liquid > 0:
      prevOrFirst_liquid = "prev"
      toGraph_liquid = 1

    if counter_calorie == 0:
      prevOrFirst_calorie = "first"
      toGraph_calorie = 0
    if counter_calorie > 0:
      prevOrFirst_calorie = "prev"
      toGraph_calorie = 1

    print "i_count_liquid: %s" % i_count_liquid
    print "i_count_calorie: %s" % i_count_calorie
    print "counter_liquid: %s" % counter_liquid
    print "counter_calorie: %s" % counter_calorie
    print "prevOrFirst_liquid variable value: %s" % prevOrFirst_liquid
    print "prevOrFirst_calorie variable value: %s" % prevOrFirst_calorie
    print "toGraph_liquid variable value: %s" % toGraph_liquid
    print "toGraph_calorie variable value: %s" % toGraph_calorie

    template_values = {
      'user_name': user_name,
      'counter_liquid': counter_liquid,
      'counter_calorie': counter_calorie,
      'prevOrFirst_liquid': prevOrFirst_liquid,
      'prevOrFirst_calorie': prevOrFirst_calorie,
      'toGraph_liquid': toGraph_liquid,
      'toGraph_calorie': toGraph_calorie,
      'whichuser': cgi.escape(user_name),
      'liquids': liquids,
      'calories': calories,
      'whichtracker': whichtracker,
    }

    print "template_values: %s" % template_values

    path = os.path.join(os.path.dirname(__file__), 'liquid_and_calorie_index.html')
    self.response.out.write(template.render(path, template_values))

class KidneyStones(webapp2.RequestHandler):
  def post(self):

    ''' date()-formatted date (for passing to Javascript) '''
    dateStr = self.request.get('datepicker');

    user_name = self.request.get('user_name')
    whichtracker = self.request.get('liquidOrCaloriesHiddenInput')

    if whichtracker == "Liquid Intake":
      liquid = LiquidIntake(parent=ndb.Key("LiquidsDrank", user_name or "*notitle*"),
                          indexer = int(self.request.get('indexer_liquid')) + 1,
                          author = user_name,
                          liqOrCal = whichtracker,
                          content = self.request.get('recentcontent'),
                          content_diff = self.request.get('contentdiff'),
                          date_entered = dateStr)
    else:
      liquid = CaloricIntake(parent=ndb.Key("CaloriesEaten", user_name or "*notitle*"),
                          indexer = int(self.request.get('indexer_calorie')) + 1,
                          author = user_name,
                          liqOrCal = whichtracker,
                          content = self.request.get('recentcontent'),
                          content_diff = self.request.get('contentdiff'),
                          date_entered = dateStr)

    print "POST calorie is: %s" % liquid
    
    liquid.put()

    print "POST: entered liquid intake (%s) have been stored." % (liquid.content_diff)

    self.redirect('/?' + urllib.urlencode({'user_name': user_name}))

application = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/storeliqData', KidneyStones)
], debug=False)