import os
import pickle
from datetime import datetime
from ConfigParser import ConfigParser
from IPython.parallel import Client

config = ConfigParser()
config.read('{0}/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))

rc = Client(packer="pickle")
dview = rc[:]
print rc.ids


@dview.remote(block=True)
def makedir(directory, base, year):
    import os
    try:
        os.makedirs("{0}/{1}".format(directory, year))
        os.makedirs("{0}/XML/{1}".format(base, year))
    except:
        pass


@dview.remote(block=True)
def fetch(directory, base, year):
    import os
    for f in files:
        fname = f.split("/")[-1]
        os.chdir("{0}/{1}".format(directory, year))
        if not os.path.exists("{0}/XML/{1}/{2}".format(base, year, fname)):
            os.system("wget {0}".format(f))
            os.system("unzip {0}".format(fname))
            os.chdir(base)
            os.system("./parse_sq.py -d XML/{0} -xmlregex {1}.xml".format(year, fname.split(".")[0]))
            os.chdir("{0}/{1}".format(directory, year))
            os.system("mv {2} {0}/XML/{1}/{2}".format(base, year, fname))


fname = open("{0}/urls.pickle".format(config.get('directory', 'sqlalchemy')), "rb")
urls = pickle.load(fname)

for year in xrange(2005, 2014):
    print year, datetime.now()
    dview.scatter("files", urls[year])
    base = config.get('directory', 'local')
    directory = config.get('directory', 'xml')
    print "  *", directory
    makedir(directory, base, year)
    fetch(directory, base, year)