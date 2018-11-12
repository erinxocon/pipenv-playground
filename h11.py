import json
import responder
import delegator

api = responder.API()


@api.route("/")
async def resolve(req, resp):
    packages = (await req.media())["packages"].split()
    packages = " ".join(packages)
    c = delegator.run(f"pipenv-resolver {packages}")
    results = c.out
    results = results.split("RESULTS:\n")[1].strip()
    results = json.loads(results)

    resp.media = {"resolved": results}


r = api.requests.post(api.url_for(resolve), data={"packages": "requests"})
print(r.json())
