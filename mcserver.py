import ConfigParser, logging, datetime, os, collections

from flask import Flask, render_template, request

import mediacloud

CONFIG_FILE = 'settings.config'
basedir = os.path.dirname(os.path.realpath(__file__))

# load the settings file
config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'settings.config'))

# set up logging
log_file_path = os.path.join(basedir,'logs','mcserver.log')
logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
logging.info("Starting the MediaCloud example Flask app!")

# clean a mediacloud api client
mc = mediacloud.api.MediaCloud( config.get('mediacloud','api_key') )

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("search-form.html")

@app.route("/search",methods=['POST'])
def search_results():
    keywords = request.form['keywords']
    now = datetime.datetime.now()
    startDate = datetime.datetime.strptime(request.form['startdate'], "%Y-%m-%d").date()
    endDate = datetime.datetime.strptime(request.form['enddate'], "%Y-%m-%d").date()
    results = mc.sentenceCount(keywords,
        solr_filter=[mc.publish_date_query( startDate, endDate),
                     'media_sets_id:1' ], split=True, 
                     split_start_date=str(startDate), split_end_date=str(endDate))

    #Thanks to Jasmin for this part of the code!

    weekly = results['split']

    sorting = collections.OrderedDict(sorted(weekly.items()))
    
    weeks = [key[:10] for key in sorting.keys()[:-3]]
    
    mentions = sorting.values()[:-3]
    
    return render_template("search-results.html", 
        keywords=keywords, sentenceCount=results['count'], startDate=startDate.strftime('%d, %b %Y'), 
        endDate=endDate.strftime('%d, %b %Y'), 
        split=sorting, weeks=weeks, mentions=mentions)

    

if __name__ == "__main__":
    app.debug = True
    app.run()
