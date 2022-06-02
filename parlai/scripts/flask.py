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

        data = request.json
        self.agent.observe({'text': data["text"], 'episode_done': False})
        response = self.agent.act()
        response_by_sent = sent_tokenize(response['text'])
        if response_by_sent[-1].find("?") != -1:
            response_by_sent[-1] = "Okay, so are you ready for our class?"
        response['text'] = ' '.join([s for s in response_by_sent])
        return {'response': response['text']}

    def run(self):
        from flask import Flask

        self.agent = create_agent(self.opt)
        app = Flask("parlai_flask")
        app.route("/response", methods=("GET", "POST"))(self.chatbot_response)
        app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    Flask.main()
