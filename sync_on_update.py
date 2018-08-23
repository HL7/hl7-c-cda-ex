from app.sync2 import sync
print "syncing with github..."
try:
    sync()
    print "syncing complete"
except Exception as e:
    print "syncing failed"
    print str(e)
