# This is the wiki controller for the lms299.
def wiki():
     """ this controller returns a dictionary rendered by the view
         it lists all wiki pages
     >>> index().has_key('pages')
     True
     """
    #  return dict()
     pages = db().select(db.wikipage.id,db.wikipage.title,orderby=db.wikipage.title)
     return dict(pages=pages)

@auth.requires_login()
def wikicreate():
     """creates a new empty wiki page"""
     form = SQLFORM(db.wikipage).process(next=URL('wiki'))
     return dict(form=form)

def wikishow():
     """shows a wiki page"""
     this_page = db.wikipage(request.args(0,cast=int)) or redirect(URL('wiki'))
     db.wikipost.page_id.default = this_page.id
     form = SQLFORM(db.wikipost).process() if auth.user else None
     pagecomments = db(db.wikipost.page_id==this_page.id).select()
     return dict(page=this_page, comments=pagecomments, form=form)


def wikisearch():
     """an ajax wiki search page"""
     return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
              _onkeyup="ajax('callback', ['keyword'], 'target');")),
              target_div=DIV(_id='target'))

@auth.requires_login()
def wikiedit():
     """edit an existing wiki page"""
     this_page = db.wikipage(request.args(0,cast=int)) or redirect(URL('wiki'))
     form = SQLFORM(db.wikipage, this_page).process(
         next = URL('show',args=request.args))
     return dict(form=form)



@auth.requires_login()
def wikidocuments():
     """browser, edit all documents attached to a certain page"""
     page = db.wikipage(request.args(0,cast=int)) or redirect(URL('wiki'))
     db.wikidocument.page_id.default = page.id
     db.wikidocument.page_id.writable = False
     grid = SQLFORM.grid(db.wikidocument.page_id==page.id,args=[page.id])
     return dict(page=page, grid=grid)


def user():
     return dict(form=auth())

def download():
     """allows downloading of documents"""
     return response.download(request, db)
     
def callback():
     """an ajax callback that returns a <ul> of links to wiki pages"""
     query = db.wikipage.title.contains(request.vars.keyword)
     pages = db(query).select(orderby=db.wikipage.title)
     links = [A(p.title, _href=URL('wikishow',args=p.id)) for p in pages]
     return UL(*links)


def news():
    """generates rss feed from the wiki pages"""
    response.generic_patterns = ['.rss']
    pages = db().select(db.wikipage.ALL, orderby=db.wikipage.title)
    return dict(
       title = 'lms299 wiki rss feed',
       link = 'http://127.0.0.1:8000/lms299/wiki',
       description = 'lms299 wiki rss feed',
       created_on = request.now,
       items = [
          dict(title = row.title,
               link = URL('show', args=row.id, scheme=True,
                      host=True, extension=False),
               description = MARKMIN(row.body).xml(),
               created_on = row.created_on
               ) for row in pages], 
        pages=pages,
        feedCreated_on=request.now)
