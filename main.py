from turtle import width
import fitz, re, copy, os
from datetime import datetime

class Redactor:
    @staticmethod
    def getFileList(path):
        files = os.listdir(path)
        all_files = []
        for entry in files:
            full_path = os.path.join(path,entry)
            if os.path.isdir(full_path):
                all_files = all_files + Redactor.getFileList(full_path)
            else:
                if ".pdf" in full_path:
                    all_files.append([full_path, entry]) #check this
        return all_files
    
    #constructor
    def __init__(self,path, output_path, regex_path, word_path):
        self.path = path
        self.output_path = output_path
        self.regex_list = open(regex_path, 'r').readlines()
        self.word_list = {}

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        with open(word_path, 'rb') as f:
            info_csv = f.read().decode(errors='replace')
            c=0
            info_csv = info_csv.split('\n')
            for line in info_csv:
                if c == 0:
                    c+=1
                else:
                    words = line.strip().replace("","").split(",")
                    if len(words) < 5:
                        for word in words:
                            if len(word) > 1 and word not in self.word_list:
                                self.word_list[word]={"status": False, "type":"none"}
                            '''
                            {
                                "vivek singh": False,
                                "chutiya" : False
                            } 
                            '''
    def check_sensitive_regex(self,text):
        #func to get all the lines
        for line in text:
            for regex_ in self.regex_list:
                pass
                #Fuckedup code
    
    def check_sensitive_words(self,text):
        white_list = ['as', 'Page', 'short']
        for line in text:
            for word in self.word_list:
                if ' ' in word and word in line:
                    self.word_list[word]["status"] = True
                elif word in line.split(" ") and word not in white_list:
                    self.word_list[word]["status"] = True
    
    def redact_files(self,files):
        for file in files:
            self.redaction(file)
    
    def redaction(self, file_name):
        #main redactor function
        doc = fitz.open(file_name[0])
        for page in doc:
            text_date = page.getText("text").split("\n")
            self.check_sensitive_regex(text_date)
            self.check_sensitive_words(text_date)

            for name in self.word_list:
                if self.word_list[name]["status"] is True:
                    print("Name: ",name)
                    areas = page.searchFor(name)
                    if areas is not None:
                        for area in areas:
                            if self.word_list[name]['type'] == "name":
                                words = name.split(" ")
                                char_width = area,width / len(name)
                                start = area.x0 + (char_width*1.3)

                                for w in words:
                                    area.x0 = start
                                    area.x1 = area.x0 + (char_width*len(w))
                                    page.addRedactAnnot(area, fill=(0,0,0))
                                    start = area.x1 + (1.3*char_width)
                            elif self.word_list[word]['type'] == 'hostname':
                                area.x1 -= 10
                                page.addRedactAnnot(area, fill=(0,0,0))
                            elif self.word_list[word]['type'] == 'ip':
                                area.x1 -= 10
                                page.addRedactAnnot(area, fill=(0,0,0))
            page.apply_redactions()
        for word in self.word_list:
            self.word_list[word]["status"] = False
        doc.save(os.path.join(output_path, file_name[1]))

if __name__ == "__main__":
    input_path = 'InputDocs'
    regex_path = 'regex_list.txt'
    word_path = 'word_list.csv'
    output_path  = os.path.join('RedactedDocs', datetime.now().strftime("%b-%d-%Y-%H-%M"))
    redactor = Redactor(input_path,output_path,regex_path,word_path)
    file_list = redactor.getFileList(input_path)
    redactor.redact_files(file_list)