
#-------moudle information manager------#

from  Database  import  *

words = (
    (1, 'walla', 1, 0),
    (2, 'google', 1, 0),
    (3, 'wikipedia', 1, 0),
    (4, 'game', 2, 0),
    (5, 'fun', 2, 0),
    (6, 'money', 3, 0),
    (7, 'value', 3, 0),
    (8, 'dollar', 3, 0),
    (9, 'bank', 3, 0)
)


class WordsHandler(object):
    words_dict = {}

    def __init__(self):
        self.database = Database()
        #self.database.insert("Words", words)
        self.words_dict = self.database.get_dict_from_table("Words")

        #self.database.printTable("WORDS")

    def common_word_and_site(self,writtin_string):
        #checks if a specific word is in the written sring and adda 1 to the dic if apears
        for word in list(self.words_dict.keys()):
            if word in writtin_string.lower():
                value = self.words_dict[word]
                self.words_dict[word] = ( value[0], value[1] + 1 )
                #print self.words_dict
                self.database.exec_query("DELETE FROM WORDS")
                self.database.set_dict_to_table("WORDS",self.words_dict)
                self.database.printTable("WORDS")
                return True
        return False







