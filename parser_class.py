# This Python file uses the following encoding: utf-8

import json


class Parse:
    name = ""
    status_key = ""
    results_file = ""


    def __init__ (self, name):
        self.name = name
        self.status_file = "./statuses/" + name + ".txt"
        self.results_file = "./results/" + name + ".json"


    def save_results(self, results):
        res = json.dumps(results)
        f = open(self.results_file, 'w', encoding='utf-8')
        f.write(res)
        f.close()


    def write_status(self, status):
        f = open(self.status_file, 'w', encoding='utf-8')
        towrite = str(status) + " links processed"
        f.write(towrite)
        f.close()
        

    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        f = open(self.status_file, 'w', encoding='utf-8')
        f.write(data)
        f.close()
