#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Example Flask server which hosts a model.

## Examples
**Serving the model**
```shell
parlai flask -m repeat_query
parlai flask -mf zoo:blender/blender_90M/model
```

**Hitting the API***
```shell
curl -k http://localhost:5000/response -H "Content-Type: application/json" -d '{"text": "foobar"}'
```
"""


import random
from datetime import datetime
random.seed(datetime.now())
class_start_sentences=[" Okay, so are you ready for our class now?", " All right, are you ready for our lesson today?", 
        " Ok, are you prepared for our lesson now?", " All right, shall we start our lesson now?"]


from parlai.core.agents import create_agent
from parlai.core.params import ParlaiParser
from parlai.core.script import ParlaiScript, register_script
from nltk.tokenize import sent_tokenize


@register_script('flask', hidden=True)
class Flask(ParlaiScript):
    @classmethod
    def setup_args(cls):
        parser = ParlaiParser(True, True)
        return parser

    def chatbot_response(self):
        from flask import request
        # print("RECEIVED")
        self.turn_cnt += 1
        data = request.headers.get("text")
        self.agent.observe({'text': data, 'episode_done': False})
        response = self.agent.act()
        # print(response)
        # rand_int = random.randint(0, 4)
        response.force_set("text", random.choice(response["beam_texts"])[0])
        response_by_sent = sent_tokenize(response['text'])
        last_question = len(response_by_sent) - 1
        find_flag = False
        class_begin = False
        for id, sent in reversed(list(enumerate(response_by_sent))):
            if sent.find("?") != -1:
                last_question = id
                find_flag = True
                break
        if (self.turn_cnt >= 3 and find_flag == True and last_question != 0) or\
                (self.turn_cnt >= 7 and find_flag == True):
            response.force_set("text", "")
            response_by_sent[last_question] = random.choice(class_start_sentences) 
            self.turn_cnt = 0
            class_begin = True
            self.agent.reset()
            for id, s in enumerate(response_by_sent):
                if id <= last_question:
                    # print(s)
                    response.force_set('text', response["text"] + s)
                else:
                    break
        # print(response)
        if class_begin:
            return {'response': "[ClassBegin]" + response['text']}
        else:
            return {'response': response['text']}

    def run(self):
        from flask import Flask
        self.turn_cnt = 0
        self.agent = create_agent(self.opt)
        app = Flask("parlai_flask")
        app.route("/response", methods=("GET", "POST"))(self.chatbot_response)
        app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    Flask.main()
