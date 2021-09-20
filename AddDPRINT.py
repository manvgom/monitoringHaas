import sys
import os
import math
import logging
import logging.config

LINE_BEFORE = 1
WORD_START = 'N10'
WORD_TOOL = 'M06'
WORD_FINISH = 'M30'

dict_variables_haas = {
'Fecha': {'variable': 3011, 'decimal': 60},
'Hora': {'variable': 3012, 'decimal': 60},
'Taladrina': {'variable': 1094, 'decimal': 62},
'RPM': {'variable': 3027, 'decimal': 62},
'DiametroReal': {'variable': 8557, 'decimal': 62},
'DesgasteLongitud': {'variable': 8554, 'decimal': 62},
'DesgasteDiametro': {'variable': 8556, 'decimal': 62},
'CronoInicioCiclo': {'variable': 3021, 'decimal': 44},
'CronoTotalHerramienta': {'variable': 8560, 'decimal': 62},
'CronoAvanceHerramienta': {'variable': 8559, 'decimal': 62}
}
def cleanTool(tool):
    clean_tool = multipleReplace(tool[1:len(tool)-2])
    logging.info(clean_tool)
    return clean_tool

def multipleReplace(word):
    word = word.replace(" ","")
    word = word.replace("_","*")
    word = word.replace("-","*")
    word = word.replace(":","*")
    return word

def get_rows_word(filename, word):
    '''
    Busca dentro del archivo la "word" por filas. Retorna las filas donde ha encontrado la palabra.
    '''
    index_lines_with_word = []
    try:
        with open(filename, 'r') as lines:
            for index_line,line in enumerate(lines):
                if word in line:
                    index_lines_with_word.append(index_line)
            return index_lines_with_word
    except AttributeError as e:
        logging.warning(f"No se ha podido leer el archivo! {e}")
        return None

def read_file(array_lines, filename, words, list_words, line_before):
    '''
    Primera vez que entra: Guarda todas las filas del documento en un array(array_lines)
    Otras veces: Añade la "word" o el array de "words" en las filas que ha leido previamente.
    '''
    line_before_n = int(line_before)
    if (array_lines == []):
        with open(filename, 'r') as read_file:
            array_lines = list(read_file)
    else:
        pass

    for list_word in list_words:
        for word in words:
            array_lines[list_word - line_before_n] += f'{word}\n'

    logging.info ("Read hecho!")
    return array_lines

def write_file(array_lines, filename):
    '''
    Passa el array(array_lines) a documento.
    '''
    filename = filename + "dprnt"
    with open(filename, 'w') as write_rows:
        for array_line in array_lines:
            write_rows.write(array_line)
    return None

def logger():
    '''
    Para poder hacer "prints" con formato
    '''
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%H:%M:%S')

def addDPRNT(colums):
    array_colum = []
    for colum in colums:
        array_colum.append(colum)
    colums_joined = '*'.join(array_colum)
    colums_dprnt = f"DPRNT[{colums_joined}]"
    row = ["", "G103 P1", colums_dprnt, "G103", ""]
    return row

def updateVariableHaas(dict_variables):
    variables = []
    for dict_variable in dict_variables:
        datos_dict_variable = dict_variables.get(dict_variable)
        variable = f"#{datos_dict_variable.get('variable')}[{datos_dict_variable.get('decimal')}]"
        variables.append(variable)
    #logging.info(variables)
    return variables

def updateIndexsHaas(dict_variables):
    indexs = []
    for dict_variable in dict_variables:
        indexs.append(dict_variable)
    indexs.insert(2,'Eina')
    indexs.insert(3,'Material')
    return indexs


def main():
    array_lines = []
    logger()
    filename = input("Copia el path del archivo? ")
    material = input("Quin material s'utilitzarà? ")

    #DPRNTs INICI
    find_row_begin_word = get_rows_word(filename, WORD_START)
    logging.info(f"El programa empieza en la línea {find_row_begin_word}")
    array_lines = read_file(array_lines, filename, addDPRNT(updateIndexsHaas(dict_variables_haas)), find_row_begin_word, LINE_BEFORE)
    array_lines.pop(1) #elimino la primera linia del gCode

    #UPDATE VARIABLES HAAS
    variables_haas = updateVariableHaas(dict_variables_haas)
    variables_haas.insert(2, material)

    #DPRNTs TOOL
    find_row_tools = get_rows_word(filename, WORD_TOOL)
    logging.info(f"Se han encontrado {len(find_row_tools)} cambios: {find_row_tools}")

    for row_tools in find_row_tools:
        variables_haas.insert(2, cleanTool(array_lines[row_tools-2]))

        array_variables = addDPRNT(variables_haas)

        array_lines = read_file(array_lines, filename, array_variables, [row_tools], LINE_BEFORE)
        array_variables.pop(2)
        variables_haas.pop(2)

    #DPRNTs FINAL
    find_row_final_word = get_rows_word(filename, WORD_FINISH)
    logging.info(f"El programa termina en la línea {find_row_final_word}")
    variables_haas.insert(2,'.')
    array_lines = read_file(array_lines, filename, addDPRNT(variables_haas), find_row_final_word, LINE_BEFORE+1)

    write_file(array_lines, filename)
    logging.info("HE TERMINADO!")
    sys.exit(0)

if __name__ == "__main__":
    main()
