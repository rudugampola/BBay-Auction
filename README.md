# CS361 - BBay Auction

<img align="right" src="https://user-images.githubusercontent.com/28117713/194800101-8d524efe-ed34-48f2-9a77-cb3b51c5bfd1.png" alt="My Image" width="400">

<p>From our humble beginnings in 2022, Bbay has grown to become the world's
largest online 🌎 marketplace 🛒, where practically anyone 👫 can bid to buy and sell 💲
practically anything. We offer the greatest selection of new and used
goods, at great prices, and with a service that is second to none 😊. </p>
<p>We are committed to providing our customers with the best possible online
shopping experience 💯. We are constantly working to improve our site and
our service, and we welcome your feedback 🔨. We hope you enjoy your shopping
experience with us, and we look forward to serving you again soon 👋.</p>
<p><i>We're not like any other online marketplace. And we're proud of that.</i></p>
<hr>
<p>Microservice</p>
REQUEST Data: The data is extracted from the database and must be serialized into a JSON dump. The data is saved to a text file named 'data.txt' located within the same folder as the microservice. The 'type' can be defined as profits, expenses, or sales to enable proper labeling for the charts.
<code>
profitsJSON = (JsonResponse({'data': list(data), 'type': 'profits'}))
# Write the JSON object to a file
with open('auctions/graphs/data.txt', 'w+') as f:
    f.write(expensesJSON.content.decode('utf-8'))
</code>
<p>
RECEIVE Data: 
The chart generated from the data will be saved at the same location as the microservice. The chart can be read as binary and displayed on a HTML page.  
    </p>
<code>
import base64

with open('auctions/graphs/graph.png', 'rb') as image_file:
    image = base64.b64encode(image_file.read()).decode('utf-8')
</code>

<img align="right" src="https://user-images.githubusercontent.com/28117713/198697906-f6a048ea-5167-4b1c-8b83-559323109b38.png" alt="Microservice UML" width="400">
