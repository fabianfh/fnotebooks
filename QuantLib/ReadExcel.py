from openpyxl import *

def get_ref(col_names,ws):

    for row in ws.rows:
        retval ={}
        for cell in row:
            for name in col_names:
                if(cell.value == name):
                    retval[name] = cell
            
        if(len(retval) == len(col_names)):
            return retval
      
    raise Exception("Could not find columns:" + str(col_names ))
      

                
def get_list_from_cols(col_names,ws):
    retval = []

    refs = get_ref(col_names,ws)
    for index in range(1,500):     
        row = {}
        for col_name in col_names:
            row[col_name] = refs[col_name].offset(index,0).value
            if (row[col_name] is None):
                return retval            
        retval.append(row)
    return retval