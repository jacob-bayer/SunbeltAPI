from SAWP import SunbeltClient
sunbelt = SunbeltClient("http://127.0.0.1:5000/graphql")

test = sunbelt.comments.first()