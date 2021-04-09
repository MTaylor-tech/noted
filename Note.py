import datetime


class Note:
  def __init__(self, iid=None, text="", created=None, updated=None):
    self.iid = iid
    self.text = text
    self.created = created
    self.updated = updated
    if self.created is None:
      self.created = self.today()
    if self.updated is None:
      self.updated = self.today()
    self.saved = True

  def today(self):
      """Grab today's date."""
      return self.get_formatted_date(datetime.date.today())

  def get_formatted_date(self, date):
      """Return a nicely formatted date like: 22 May 2021."""
      format_str = '%d %b %Y'
      otherformat_str = '%Y-%m-%d'
      return (datetime.datetime.strftime(datetime.datetime.strptime(
          ('%s' % date)[0:10], otherformat_str).date(), format_str))

  def update(self, text):
      self.text = text
      self.updated = self.today()
      return self

  def append(self, ch):
      self.text += ch
      self.saved = False
      self.updated = self.today()

  def backspace(self):
      self.text = self.text[:-1]
      self.saved = False
      self.updated = self.today()

  def encode(self):
      self.text = self.text.replace("'", "''").replace('"', '""')

  def decode(self):
      self.text = self.text.replace("''", "'").replace('""', '"')
