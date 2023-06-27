# BNC
Bercley Nucleonics Gui

Interface to control via Bercley Nucleonics controler

Test with model 505 on win 10

## Requirements
*   python 3.x
*   Numpy
*   PyQt6
*   Pyvisa pin install pyvisa (https://pyvisa.readthedocs.io/en/latest/)
*   qdarkstyle (https://github.com/ColinDuquesnoy/QDarkStyleSheet.git)
    * pip install qdarkstyle. 
 
  
  ## Usages   
  appli=QApplication(sys.argv)
  
  tt=BNCBOX()
  
  tt.show()
  
  appli.exec()   
  
