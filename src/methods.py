import json
import traceback
import os
from dotenv import load_dotenv
class Generator:
    def getPage(self, instructor, params):
        try:
            # Load config file
            config=self.read_file("json/system/config.json","json","//")
            if str(config).split()[0] == "FileNotFoundError:":
                return ("Config File not found")
            # Load instructor File
            if config['INSTRUCTORS_FOLDER'] == "@@template" :
                instructor_path=config['TEMPLATES_FOLDER'] + config['CURRENT_TEMPLATE'] +  'instructors/'
            else:
                instructor_path=config['INSTRUCTORS_FOLDER']
            instructor_data=self.read_file(instructor_path + instructor,"text","//")
            if str(instructor_data).split()[0] == "FileNotFoundError:":
                return ("Instructor file not found: " + str(instructor_data).split()[1])
            # substitute all the params instances
            for key in params:
                instructor_data=instructor_data.replace("{"+str(key)+"}",str(params[key]))
            # substitute all the {{VAR}} chunks
            # using list comprehension + startswith()
            # All occurrences of substring in string
            instructor_data=self.metavariables(instructor_data, config['METAVARIABLES_FOLDER'])
            instructions=json.loads(instructor_data)
            #load layout
            layout_stream=self.read_file("templates/" + config["CURRENT_TEMPLATE"] +  config["LAYOUTS_FOLDER"] +  instructions['layout'],"text")
            if str(layout_stream).split()[0] == "FileNotFoundError:":
                return ("Layout file not found: " + str(layout_stream).split()[1])
            for key in instructions['single_values']:
                layout_stream=layout_stream.replace("{{@" + str(key) + "}}", str(instructions['single_values'][key]))
            for key in instructions['sections']:
                if instructions['sections'][key]['type'] == "disabled":
                    layout_stream=layout_stream.replace("{{@" + str(key) + "}}", "")
                elif instructions['sections'][key]['type'] == "content_file":
                    view_stream=self.read_file("templates/" + config["CURRENT_TEMPLATE"] + instructions['sections'][key]['view_file'],"text")
                    if str(view_stream).split()[0] == "FileNotFoundError:":
                        return ("View file not found: " + str(view_stream).split()[1])
                    content_json=self.read_file(instructions['sections'][key]['content_file'],"json","//")
                    if str(content_json).split()[0] == "FileNotFoundError:":
                        return ("Content file not found: " + str(content_json).split()[1])
                    for element in content_json:
                        if (type(content_json[element]) is str):
                            view_stream=view_stream.replace("{{@" + element + "}}", str(content_json[element]))
                        elif (type(content_json[element]) is dict):
                            try:
                                #psm - populated section marker
                                #esm - empty section marker
                                psm1_1=view_stream.find('{{#'+ element + '}}')
                                psm1_2=view_stream.find('{{#'+ element + '}}') + len('{{#'+ element + '}}')
                                psm2_1=view_stream.find('{{/'+ element + '}}')
                                psm2_2=view_stream.find('{{/'+ element + '}}') + len('{{/'+ element + '}}')
                                populated_subtemplate_with_marks = view_stream[psm1_1:psm2_2]
                                populated_subtemplate_content= view_stream[psm1_2:psm2_1]
                                esm1_1=view_stream.find('{{#'+ element + '_empty}}')
                                esm1_2=view_stream.find('{{#'+ element + '_empty}}') + len('{{#'+ element + '_empty}}')
                                esm2_1=view_stream.find('{{/'+ element + '_empty}}')
                                esm2_2=view_stream.find('{{/'+ element + '_empty}}') + len('{{/'+ element + '_empty}}')
                                empty_subtemplate_with_marks = view_stream[esm1_1:esm2_2]
                                empty_subtemplate_content= view_stream[esm1_2:esm2_1]
                                subtemplate_out=''
                                if len(content_json[element]) > 0:
                                    for subelement in content_json[element]:
                                        #subtemplate_out+= str(content_json[element][subelement]['author_name'])
                                        if "@subtemplate" in content_json[element][subelement]:
                                            partial=self.read_file(content_json[element][subelement]['@subtemplate'],"text")
                                        else:
                                            partial=populated_subtemplate_content
                                        for subattrib in content_json[element][subelement]:
                                            partial=partial.replace('{{@'+element+':'+subattrib+'}}',content_json[element][subelement][subattrib])
                                        subtemplate_out+=partial
                                    view_stream=view_stream.replace(populated_subtemplate_with_marks,subtemplate_out)
                                    view_stream=view_stream.replace(empty_subtemplate_with_marks,'')
                                else:
                                    view_stream=view_stream.replace(populated_subtemplate_with_marks,'')
                                    view_stream=view_stream.replace(empty_subtemplate_with_marks,empty_subtemplate_content)
                            except Error:
                                # not found in the original string
                                subtemplate = '' # apply your error handling
                    layout_stream=layout_stream.replace("{{@" + key + "}}",view_stream)
                elif instructions['sections'][key]['type'] == "parameted_file":
                    view_stream=self.read_file("templates/" + config["CURRENT_TEMPLATE"] + instructions['sections'][key]['view_file'],"text")
                    for element in instructions['sections'][key]['parameters']:
                        view_stream=view_stream.replace("{{@" + element + "}}", str(instructions['sections'][key]['parameters'][element]))
                    layout_stream=layout_stream.replace("{{@" + key + "}}",view_stream)
                else:
                    #Direct file
                    view_stream=self.read_file("templates/" + config["CURRENT_TEMPLATE"] + instructions['sections'][key]['view_file'],"text")
                    layout_stream=layout_stream.replace("{{@" + key + "}}",view_stream)
            return layout_stream
            #return a
        except Exception as e:
            return traceback.format_exc()
            #return "lolo:" + str(e)


    def read_file(self, filename, mode, comment_string=""):
        try:
            with open(filename,"r") as handler:
                if comment_string=="":
                    stream=''.join(line for line in handler)
                else:
                    stream=''.join(line for line in handler if not line.lstrip(' ').startswith(comment_string))
                if mode == 'json':
                    return json.loads(stream)
                else:
                    return stream
        except FileNotFoundError :
            return "FileNotFoundError: " + filename

    def metavariables(self, stream, metavariables_path):
        from functools import reduce
        var_positions = [i for i in range(len(stream)) if stream.startswith('{{VAR}}', i)]
        #position=1
        #for position in range(2):
        #return stream
        variable_with_marks=[]
        variable_content=[]
        for position in range(len(var_positions)):
            vm1_1=stream.find('{{VAR}}',var_positions[position])
            vm1_2=vm1_1 + 7
            vm2_1=stream.find('{{/VAR}}',var_positions[position])
            vm2_2=vm2_1 + 8
            variable_with_marks.append(stream[vm1_1:vm2_2])
            variable_content.append(stream[vm1_2:vm2_1])

        for position in range(len(var_positions)):
            var_elements=variable_content[position].split("|")
            var_file=metavariables_path + var_elements[0]
            #element=var_elements[1].split(':')
            var_json=self.read_file(var_file,"json","//")
            stream=stream.replace(variable_with_marks[position],reduce(lambda x,y : x[y],var_elements[1].split(":"),var_json))
            #stream=stream.replace(variable_with_marks[position],var_json[var_elements[1]])
        return stream

