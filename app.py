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
from flask import Flask, request
from flask_restful import Resource, Api
from parlai.core.opt import Opt


agent = create_agent({"mf": "zoo:blender/blender_90M/model"})
app = Flask(__name__)
api = Api(app)

class Response(Resource):
    def get(self):
        data = request.headers.get("data")
        agent.observe({'text': data, 'episode_done': False})
        response = agent.act()
        return {'response': response['text']}


api.add_resource(Response, '/response')


if __name__ == "__main__":
    app.run(debug=True)
