import os
import json
from string import Template
from datetime import datetime
from pprint import pprint
from aiohttp import web


from collections import defaultdict 


async def hello(request):
    return web.Response(text=get_text(), content_type="text/html")


def get_text():
    prev_answers = render_responses()

    INTRO_TEXT = """
welcome to my antisocial counter.


i believe i am the object of a social network hack, that happened some time ago.

to test my theory, this is an anonymous question/poll 

    """

    TEXT = f""" 
<html>
<script>

  function doclick() {{
//
}}

</script>
<pre>

hi 

{INTRO_TEXT}

<!--<form action="/post" method="POST"> -->
<form action="/post" method="POST"> 
Question 1: Have you or your network been approached, contacted 
or interacted with by anyone claiming to be speaking on my or my 
network's behalf? Maybe running a study, running an investigation, 
running surveillance, running probation, running an
experiment, perhaps from the press, from the police, from the intelligence 
services, or any other organisation or individual whether this was 
directly or indirectly, outright or implied via contact that was 
physical, electronic or online? 

This may have been over the last 12 years.


<input type=radio name="q1yes">Yes.</input>
<input type=radio name="q1no">No. Absolutely not. No way. Never. How would it work?</input>


Question 2: Do you suspect whether you have also been the target of
such an hack.

<input type=radio name="q2yes">Yes.</input>
<input type=radio name="q2no">No. Absolutely not. No way. Never. How would it work?</input>


Message:
<textarea name=message size=15 rows=5 cols=30> </textarea>
<label> Show message to all <input type=checkbox name="message_public"></input> </label>
<!--<input type=submit onclick="doclick();"></input>-->
<input type=submit value="Submit"></input>
</form>






Previous answers:
{prev_answers}
</pre>

</html>
    """
    return TEXT

def log_response(answers, date, message, message_public):
    date_j = json.dumps(date)
    answers_j = json.dumps(answers)
    message_j = json.dumps(message)
    message_public_j = json.dumps(message_public)
     
    template = Template("""
          {"answers": $answers_j, "date": $date_j, "message": $message_j, "message_public": $message_public_j}
    """)
    result = template.substitute(answers_j=answers_j, date_j=date_j, message_j=message_j, message_public_j=message_public_j)

    with open('data.log', 'a') as f:
        f.write(result)

def get_responses():
    results = {}
    #results["messages"] = []
    full_results = [] 
    log_name = 'data.log'

    if not os.path.exists(log_name):
        return {}, {}

    with open('data.log', 'r') as f:
        data = f.read()

    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue

        try:
            entry = json.loads(line)
        except Exception as e:
            print(f"parse error for {line}")
            continue
        
        if entry.get("message"):
            if entry.get("message_public"):
                full_result = {"message": entry.get("message"), "date": entry.get("date")}
            else:
                full_result = {"message": "message private", "date": entry.get("date")}
        else:
            full_result = {"date": entry.get("date")} 
            
        
        
        print(entry.get('answers') )
        for k, v in entry.get('answers', {}).items():
            if k not in results:
                results[k] = 1
            else:
                results[k] += 1
            full_result[k] = v

        full_results.append(full_result)

    print(results)
    return results, full_results
    

def render_responses():
    r, fr = get_responses()        
    lines = [json.dumps(afr) for afr in fr]
    fr = "\n".join(lines)

    t = Template("""

Totals:    

$r

Responses:

$fr 
""")
    return t.substitute(r=r, fr=fr)

async def post_handler(request):
    data = await request.post()
    print(data)
    # answer_cat = ["q1yes", "q1no", "q2yes", "q2no", "message"]
    message = data.get('message', "")
    message_public = data.get('message_public', "")
    answers = {k: v for k, v in data.items() if k not in ("message", "message_public") }
    date = str(datetime.now())
    log_response(answers, date, message, message_public)
    
    return web.Response(text="""thanks for submitting. click <a href="/"> here </a> to go back to the main page""", content_type="text/html")


app = web.Application()
app.add_routes([web.get("/", hello), 
    web.post('/post', post_handler),])

#get_responses()
print(render_responses())
web.run_app(app, port=80)
#web.run_app(app )
