#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil

root = os.getcwd()
#total_list = 0

def htmlResult(path_result,total_list=0):
    #print path_result
    html = open('index.html', 'w')
    html.write("""
      <html>
         <head>
           <head>
              <meta charset="UTF-8">
              <script language="javascript">

                 function setUrl(str){
                   //alert("in getUrl method");
                   //alert(str);


                   // get total list from html
                   var total_pages = document.getElementById("total").innerHTML;
                   //alert("total_pages...: "+total_pages);

                   var old_url = document.getElementById("pic").src;   // current img src
                   //alert(old_url);
                   
                   var new_url = "";
                   var old_str_num = "";
                   var old_int_num = 0;
                   var new_int_num = 0;
                   var old_str = "";
                   var new_str = "";
                   
                   // set new img src
                   var under = old_url.lastIndexOf("_")
                   var colon = old_url.lastIndexOf(".")

                   old_str_num = old_url.substring(under+1,colon);
                   old_int_num = parseInt(old_url.substring(under+1,colon));

                   old_str = "_" + old_str_num + ".JPG";
                   new_str = "_" + new_int_num + ".JPG"
 

                   if(str == "pre"){
                     if(old_str_num == "1"){
                      alert("It's already the first page!");
                     }
                     else{
                      new_int_num = old_int_num  - 1;
                      new_str = "_" + new_int_num + ".JPG";
                      new_url = old_url.replace(old_str, new_str); // new img src
                      document.getElementById("pic").src = new_url; 
                     }
                   }

                   if(str == "first"){
                      //alert("go to the first page!!");
                      if(old_str_num == "1"){
                        alert("It's already the first page!!!");
                      }
                      else{
                        new_str = "_1.JPG"; 
                        new_url = old_url.replace(old_str, new_str); // new img src
                        document.getElementById("pic").src = new_url;
                      }
                      
                   }

                   if(str == "next"){
                     //alert("go to the next page");
                     if(old_str_num == total_pages){
                        alert("It's already the last page!!!");
                      }
                     else{
                         new_int_num = old_int_num  + 1;
                         new_str = "_" + new_int_num + ".JPG"
                         new_url = old_url.replace(old_str, new_str); // new img src
                         document.getElementById("pic").src = new_url; 
                      }
                   }
                 
                   if(str == "last"){
                     //alert("go to the last page!!!");
                     if(old_str_num == total_pages){
                       alert("It's already the last page!!!");
                     }
                     else{
                       new_str = "_"+ total_pages + ".JPG";
                       new_url = old_url.replace(old_str, new_str); // new img src
                       document.getElementById("pic").src = new_url;
                     }
                   }   
                 }
              
                 function previous(){
                   setUrl("pre");
                 }

                 function first(){
                   setUrl("first");
                 }

                 function next(){
                    setUrl("next");
                 }

                 function last(){
                    setUrl("last");
                 }
              
              </script>

              <style>
                body{
                   background-color:#c0c0c0;
                   text-align:center;
                }

                img{width:66%;}
                
              </style>
              
              </head>
         </head>
      <body>
      <div style="width:100%;">
      """)

    files = os.listdir(path_result)
    
    for file in files:
        #print file
        if file.endswith('.JPG'):
            #global total_list
            total_list +=1
            file_path = path_result + "\\" + file
            print file_path
            if total_list == 1:
                html.write('<center><div style="width:66%;margin-top:6%;">') 
                #html.write("<img id='pic' src='%s' /></div></center>" % file_path)
                html.write("<div><img id='pic' src='%s' />" % file_path)
                html.write('</div>')
            #break

    #print total_list
    #html.write('</br></br></br></br></br></br>')
    #html.write('<center>')  ## <div style="width:100%;"><div sytle="width:64%">
    html.write('<div style="background-color:#F4F4F4; width:66%; height:38px; border:1px solid #B9B9BA">')
    html.write('<div style="float:left; padding-left:4%; padding-top:1%;"><input type="image" id="first" src="C:\\picture\\first.PNG"  onclick="first()" /></div>&nbsp;&nbsp;&nbsp;&nbsp;')
    html.write('<div style="float:left; padding-left:4%; padding-top:1%;"><input type="image" id="pre" src="C:\\picture\\pre.PNG" onclick="previous()" /></div>&nbsp;&nbsp;&nbsp;&nbsp;')
    html.write('<div style="float:left; padding-left:4%; padding-top:1%;"><input type="image" id="next" src="C:\\picture\\next.PNG" onclick="next()" /></div>&nbsp;&nbsp;&nbsp;&nbsp;')
    html.write('<div style="float:left; padding-left:4%; padding-top:1%;"><input type="image" id="last" src="C:\\picture\\last.PNG" onclick="last()" /></div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
    html.write('</center>')
    html.write('<p id = "total" hidden>')
    html.write(str(total_list))
    html.write('</p>')
    html.write('</div></div></div>')
    html.write('</body></html>')
    html.close()
    copyFileToDes(path_result)
    ##print total_list
    

def copyFileToDes(path_result):
    html_path = path_result + "\\index.html"
    if os.path.isfile(html_path):
        os.remove(html_path)
    shutil.move(root + "\\" + "index.html", path_result)


#path_result = sys.argv[1]
#print path_result
#htmlResult(path_result)
