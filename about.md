# Overview

Feel free to say no or suggest improvements, but what we are asked to do, OCR+TTS its approx 6 lines of python and 50 lines of Java/Kotlin its too simple

So if you want to make something cool this is my proposed design

# Feature Recommendations
All the features/functions recommendations:-

<div style="margin-left: 4em">
<table>
        <tr><th>Feature</th><th>Priority</th><th>Explanation</th></tr>
        <tr><td>Calender</td><td>L0</td><td>A calender at backend to enable reminders</td></tr>
        <tr><td>Reminder</td><td>L0</td><td>Set a reminder to do something</td></tr>
        <tr><td>Timer</td><td>L0</td><td>Nothing much to do in backend, just a timer UI</td></tr>
        <tr><td>Weather</td><td>L0</td><td>Speak out the fetched weather</td></tr>
        <tr><td>Emergency</td><td>L0</td><td>Calls a trusted one, other safety features</td></tr>
        <tr><td>OCR from Image</td><td>L0</td><td>Speak out whats written on image</td></tr>
        <tr><td>OCR from Documents</td><td>L0</td><td>Speaks out whats written on a document</td></tr>
        <tr><td>A guessing game</td><td>L0</td><td>Classic guessing game, hot or cold</td></tr>
        <tr><td>Random Facts</td><td>L0</td><td>Speak out some random facts</td></tr>
        <tr><td>Random Jokes</td><td>L0</td><td>Speak out some random jokes</td></tr>
        <tr><td>Text Editor</td><td>L1</td><td>Makes changes in place to uploaded txt</td></tr>
        <tr><td>Pdf Editor</td><td>L2</td><td>Makes changes to uploaded pdf</td></tr>
        <tr><td>More Document Viewing Support</td><td>L2</td><td>Listen to wide variety of docs</td></tr>
        <tr><td>Event Summarizer</td><td>L3</td><td>Speak out summary of some issue user asks about</td></tr>
        <tr><td>More Document Editing Support</td><td>L4</td><td>Make changes to wide variety of docs</td></tr>
</table>
</div>
            

Few Key Points and design choices:- 

1. The ISSUE:- 

    - Their is no reason for this project to be done in python, the kit i discussed Googles' ML Kit it itself is capable enough to **DO ALMOST EVERY ACCESSIBILITY FEATURE WE CAN THINK ABOUT**
    
    - Even if we do choose to send manual api requests or something it would be too expensive
    
    - Making any OCR, AI, TTS, Speech Synthesizer of our own is very much out of our **paygrade and/or capabilities**

2. So to mantain atleast a bit of quality or **ORIGINALNESS** given below are the modules recommendations:-

    - Voice shall be the main mode of communication:- 
    
        - Basic Workflow:- 

            ~~~
            Frontend App => Google ML Kit does the voice to text => Json Payload => Gets Lexed/Parsed in the python backend => Does the work => Sends back processed text/file        
            ~~~
        Everything i say from now on is about the backend, the frontend shall be just a thin layer, a kotlin/java app, 
        that can use Google ML Kit for TTS and Speech-to-text and sends it back as a json payload
        
        1. Reciever-Module:-
         
            - Example payload structure from frontend

              ```
                {
                  "app":{
                      "version":"0.1.0",
                      "epoch": 0,
                      "release": 0
                  },
                  "usr_details":{
                      "name":"XYZ",
                      "calender_id":"uid",
                      "input":{
                          "type":{
                              "text":true,
                              "document":false,
                              "image":true
                          },
                          "document_name": "",
                          "image_id": "UID",
                          "text_content": "HELLO"
                      },
                      "stt_confidence":0.94,
                      "timezone":"Asia/Krasnoyarsk",
                      "location": "City name"
                  }
              }
        
              ```

            - A reciever program will listen to a port on LAN and accept this type of payload from any user then call the text parser if text is not ""
            
            - If stt_confidence is less than 0.50 then ask the user again
            

        2. Text Lexer/Parser:-
        
            We need a pipeline of tools for this, classic regex first then LLM fallback if nothing can be resolved

            But somewhat basic outline for regex search shall be:- 

            ```
                #VERY BASIC WORKFLOW DONT TAKE TOO MUCH INSPIRATION FROM

                #for intent finding

                import re
                from dataclasses import dataclass

                intent_rules=[("weather.get",r"\b(weather|forecast|temperature|raining|hot)\b"),...]
                #Scalibility must be made sure of so regex + resolution shall be in a list of tuples, that can be extended anytime

                text=recieve()
                text=text.lower().strip()
                for intent,pattern in intent_rules:
                    if re.search(pattern,text):
                        #FOUND LOGIC
                #NOT FOUND LOGIC
            ```

            For LLM help fallback:-
            
            ```
                import requests
                ollama_url="MINE LISTENS ON LAN:8080/api/model"
                intents=[("weather.get",r"\b(weather|forecast|temperature|raining|hot)\b"),...]

                prompt=("classify into one of: "+",".join(intents)+".\n"+f"User said: {user.text} \n return only intent name.")
                r=request.post(...)
                result=r.json(["response"].strip().split()[0])
                #Validate the result
                #DO SOMETHING WITH result
            ```

        3. Calender:- 

            >*Needs more planning*

            I need some recommendations should i build it in C/Rust? a Python calender will have terrible performance

            OR we can implement a fake calender,  leveldb/sqlite3 databases that just holds dates+entries under that date+who. Probably Sqlite3 is better for this sorta use cases, but give me your recommendations

            -Level DB entry basic structure:- 
                
            ~~~
                "uid":{
                    "number_of_entries":23
                }
            ~~~
                "event_id@uid":{
                    "date":"TIMESTAMP",
                    "about":"WHY the reminder",
                }
        

            I cannot think about the sqlite3 table schema, give your ideas later

            -New calender instance creation json pack:- 

                ```
                {
                    "intent":"calender.create",
                    "data":{
                        "event_id":"evt-2",
                        "task": "Hello World",
                        "when": "TIMESTAMP",//local userdevice timestamp converted to system time
                        "recurrence": ""//"" or everyday or weekdays or everyconsecutivedays
                    }    
                }
                ```

        
                
        4. Reminder:- 

            - a list of reminder id's for searching the db

            - Example json for storing:-
                
                ```
                {
                    "uid": "usr_id"
                    "intent": "reminder.list",
                    "data":{
                        "reminders":[
                            "evt-2",
                            "evt-3"
                        ],
                    "count":2
                    }
                }
                ```

            - Deleting a recurring reminder is a critical action @

        5. Weather:- 

            - The location comes with the recieved json payload from user.\
            - If location is "" use server location to get weather
            - If location is "given" use recieved location.\
            - Shall use *WeatherAPI* for this.

            - Example processed json from weather data:- 
                ```
                {
                    "intent": "weather.get",
                    "data":{
                        "location": "XYZ",
                        "temp_c":23.3,
                        "feels_like_c": 32,
                        "condition": "partly cloudy",
                        "humidity": 70,
                        "wind_kph":12,
                        "sunset":"18:12",
                        "sunrise":"04.05"
                    }
                }
                ```
                
            - We can may as well allow user to ask when its gonna be dark, weather.sunset.get/weather.sunrise.get intent

        6. Read from image:- 

            - Example procesed json for tasks to be performed:- 

                ```
                {
                    "intent":"image.read",
                    "data":{
                        "image_id":"img-01"
                    }
                }
                ```

            - Gonna use paddleOCR for text recognization, b/w conversion automatically no waiting for result as recomputation is more expensive

        7. Read from txt-file:-

            - Example processed json for tasks to be performed:- 

                ```
                {
                    "intent":"textfile.read",
                    "data":{
                        "file_id":"file-01"
                    }
                }
                ```
            - Just return whats written in the txt file

        8. Read from pdf-file:- 

            - Its easier than most percieve, pdf is just a container of image and text objects, so basically OCR+ text parsing item by item in order

            - Example processed json for tasks to be performed:- 

                ```
                {
                    "intent":"pdf.read",
                    //the type pdf or not shall be inferred from the uploaded file
                    "data":{
                        "file_id":"file-02"
                    }
                }
                ```
        9. FunFact:-

            >Open Ended Question:- Should their be a intent "funfact.write"?
            - Just read out of a pre set text file/data structure of fun-facts
            - Example processed json for tasks to be performed:- 
                ```
                {
                    "intent":"funfact.read",
                    "data":{
                        "file": "Path to file of funfacts"
                    }
                }
                ```
        10. Jokes are basically the same as funfact logic, Also i wanna know if jokes.write is a good idea

        11. Game:- 

            - Generate a random number server side, ask user to guess, say hot or cold depending on proximity

            - Example processed json for tasks to be performed:- 
                ```
                {
                    "intent":"game.play"
                }
                ```
            - Starting a thread for each instance is easier
            - Probably should add a feature where computer guesses and user chooses

            -Example processed json for that:- 
            
                ```
                {
                    "intent":"game.guess"
                }
                ```

        12. SOS:-

            - User shall have a option to add a emergency number, its kv pair at database shall be "uid@sosph": "+xxxxxxxxxxxx"
            - Now dialing phone needs complex android permissioning, or idk, probably should deal with sending a whatsapp message or some crap like that
            - Its India not America
            - It shall have a cancel period(3 Sec)
    
        >This topic shall be discussed upon in future

        13. Return Payload:-

            -Shall be discussed upon later

        14. Summarizer:- 

            - Computationally too expensive locally, shall be discussed upon later
            
---

>@A basic design choice shall be asking the user for confirmation for any critical action
                   
