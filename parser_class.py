
class Parse:
    name = ""
    status_key = ""
    results_file = ""


    def __init__ (self, name):
        self.name = name
        self.status_file = name + "_st.txt"
        self.results_file = name + "_res.json"


    def save_results(self, results):
        res = results.encode('utf-8')
        f = open(self.results_file, 'w')
        f.write(res)
        f.close()


    def write_status(self, status):
        f = open(self.status_file, 'w')
        towrite = str(status) + " links processed"
        f.write(towrite)
        f.close()
        

    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        f = open(self.status_file, 'w')
        f.write(data)
        f.close()
