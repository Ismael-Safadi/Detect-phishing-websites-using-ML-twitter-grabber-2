
from xlwt import Workbook
import xlrd
from xlutils.copy import copy
class Write_in_Excel:
     def __init__(self):
         self.workbook1 = Workbook()
         try:
             workbook = xlrd.open_workbook('result.xls', formatting_info=True)
         except:
             self.sheet = self.workbook1.add_sheet('Results')
             self.header = ["Date","tweet","User","No. likes", "No. Retweets","Country","Device","URL"]
             c = 0
             for value in (self.header):
                 self.sheet.write(0, c, value)
                 c+=1
             self.workbook1.save("result.xls")
     def Write_in_Excel_File(self,row_row, SaveFilePath):
        """ Write in  Excel sheet file

                Args:
                    row(list of lists) : list of lists , (list of rows that exists in excel file)
                    SaveFilePath(str) : path to save excel file

                """



        workbook = xlrd.open_workbook('result.xls',formatting_info=True)
        worksheet = workbook.sheet_by_index(0)
        r = (worksheet.nrows)
        wb = copy(workbook)
        print(r)

        c = 0
        sheet = wb.get_sheet(0)
        for value in (row_row):
            sheet.write(r, c, value)
            c += 1

        try:
            wb.save(SaveFilePath)
        except Exception as e :

            print("cant save !" , e )
            pass

#
# E = Write_in_Excel()
# E.Write_in_Excel_File(["fjkgkf","ergerg","gergerg","gergtghtrerge","hgerger","gerwger","edghrege","ergreger"],"result.xls")