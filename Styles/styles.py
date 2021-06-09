BOX_STYLE = """
			{}{{
			    color: rgb(58, 58, 58);
			    background-color:  rgb(248, 237, 227);
			    border-style: outset;
			    border-width: 2px;
			    border-radius: 3px;
			    border-color: rgb(89, 89, 89);
			}}
			"""

BTN_STYLE = """
			QPushButton {{
			    color: rgb(58, 58, 58);
			    background-color:  rgb(248, 237, 227);
			    border-radius: {}px;
			    border-bottom: {}px solid rgb(209, 202, 194);
			}}
			QPushButton:pressed {{
			    border-top: 4px solid transparent;
			    border-bottom: 1px solid transparent;
			}}
			"""

COUNTDOWN_STYLE = """
				  color: rgb(214, 214, 214);
				  border-radius: 8px;
				  background-color: rgb(214, 77, 79);
				  """

LAYOUT_BG = "background-color: rgb(214, 77, 79);"

MAIN_BG = "QMainWindow{background-color: rgb(203, 73, 75);}"

TEXT_STYLE = "color: rgb(214, 214, 214);"

TODOLIST_STYLE = """
                QTabWidget {
                  background: #f2f1dc;
                 }

                QTabWidget::pane {
                    border: 1px solid black;
                    top:-1px; 
                    background: rgb(203, 73, 75); 
                  } 
                            
                QTabBar::tab {
                   background: #f2f1dc;
                   border-radius: 1px;
                   border-top: 0.5px gray;
                   border-bottom: 0.5px solid gray;
                   border-left: 1px solid gray;
                   padding: 9px;
                } 
                            
                QTabBar::tab:selected { 
                  background: #eaeade;
                  border-radius: 1px;
                  border-bottom: 0.5px solid gray; 
                }
                """