#Python by Timothy Kravets
#curl -X POST http://localhost:5005/newpackage -H "Content-Type: application/json" -d '{"sender": "Tim", "delivery": "SWR101", "pickup": "SWR100", "recipient" : "Chris"}'

#curl -X POST http://localhost:5005/newpackage -H "Content-Type: application/json" -d '{"sender": "Tim"}'

from flask import Flask
from flask import request
from flask import jsonify
import uuid
from flask import render_template


app = Flask(__name__)

idNum = 0

class Package:
    idNum = 0
    sender = " "
    recipient = " "
    pickup = " "
    delivery = " "
    status = " "

    def __init__(self, sender, recipient, pickup, delivery):
        self.idNum = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.pickup = pickup
        self.delivery = delivery
        self.status = "unassigned"

    def __str__(self):  
        return  "Package ID: " + self.idNum + "   From: " + self.sender + " in " + self.pickup + "   To: " + self.recipient + " at " + self.              delivery + "   Status: " + self.status
        

class Robot:
    idNum = 0
    status = "available"

    def __init__(self):
        self.idNum = str(uuid.uuid4())

    def __str__(self):
        return "Robot ID: " + self.idNum + "   Status: " + self.status

p1 = Package("Tim", "Chris", "SWR 100", "SWR 101")
p2 = Package("Chris", "Tim", "SWR 101", "SWR 100")
p3 = Package("Tim", "Wallie", "SWR 100", "SCB 420")

r1 = Robot()
r2 = Robot()
r3 = Robot()
r4 = Robot()

packages = [p1,p2, p3]
deliveries = {}
robots = [r1, r2, r3]
packIds = [p1.idNum, p2.idNum, p3.idNum]

@app.route('/', methods=['GET'])
def index():  
    return render_template('index.html', packages=packages, robots=robots)

@app.route('/v1/packages', methods=['POST'])
def registerPackage():
    data = request.json
    p = Package(data.get("sender"), data.get("recipient"), data.get("pickup"), data.get("delivery"))
    packages.append(p)
    packIds.append(p.idNum)
    response = {"id": p.idNum,
                "sender": data.get("sender"),
                "recipient": data.get("recipient"),
                "pickup": data.get("pickup"),
                "delivery": data.get("delivery")};
    return jsonify(response),201

@app.route('/v1/deliveries', methods=['POST'])
def registerDelivery():
    data = request.json
    response = " "
    for i in range(0, len(packages)):
        if (packages[i].status == "unassigned"):
            for j in range(0, len(robots)):
                if (robots[j].status == "available"):
                    deliveries[packages[i].idNum] = robots[j].idNum
                    packages[i].status = "assigned"
                    robots[j].status = "PENDING_PICKUP"
                    response = {"packageId": packages[i].idNum,
                        "sender": packages[i].sender,
                        "recipient": packages[i].recipient,
                        "pickup": packages[i].pickup,
                        "delivery": packages[i].delivery,
                        "robotId": robots[j].idNum,
                        "packageStatus": packages[i].status,
                        "robotStatus" : robots[j].status};
                    return jsonify(response),201
            print("All robots are busy")
            return jsonify(response),201
    print("All packages are assigned")
    return jsonify(response),201

@app.route('/', methods=['GET'])
def hello():
    # Passing the existing lists to the template
    return render_template('index.html', packages=packages, robots=robots)

@app.route('/v1/packages', methods=['GET'])
def allPackages():
    allElems = []
    for i in range(0, len(packages)):
        elem = packages[i]
        allElems.append(str(elem))
    return jsonify(allElems), 200

@app.route('/v1/packages/<packId>', methods=['GET'])
def findPackageById(packId):
    response = " "
    print(packId)
    for i in range(0, len(packages)):
        if (packages[i].idNum == packId):
            response = {"id": packId, "status": packages[i].status};
            break
        else:
            print("Package does not exist")
    return jsonify(response),200

@app.route('/v1/packages/<name>', methods=['GET'])
def findPackageByRec(name):
    response = " "
    print(name)
    for i in range(0, len(packages)):
        print(packages[i].recipient)
        if (packages[i].recipient == name):
            response = {"status": packages[i].status, 
                "sender": packages[i].sender,
                "recipient": name,
                "pickup": packages[i].pickup,
                "delivery": packages[i].delivery};
            break
        else:
            print("Recipient does not have any pending packages")
    return jsonify(response),200

@app.route('/v1/packages/<packId>', methods=['POST'])
def cancelPackage(packId):
    response = " "
    for i in range(0, len(packages)):
        if packId in deliveries:
            robotID = deliveries[packId]
            for j in range(0, len(robots)):
                if robots[j].idNum == robotID:
                    if (robots[j].status == "PENDING_PICKUP"):
                        packages.pop(i)
                        deliveries.pop(packId)
                        response = {"id": packId, "status": "cancelled"};
                        break
                    else:
                        print("Package has been picked up")
            else:
                print("Robot does not exist")
        elif (packages[i].idNum == packId):
            packages.pop(i)
            response = {"id": packId, "status": "cancelled"};
            break
    else:
        print("Package does not exist")
    return jsonify(response),200

@app.route('/v1/robots', methods=['GET'])
def findRobots():
    allElems = []
    for i in range(0, len(robots)):
        elem = robots[i]
        allElems.append(str(elem))
    return jsonify(allElems), 200

@app.route('/v1/deliveries', methods=['GET'])
def findDeliveries():
    return jsonify(deliveries), 200

@app.route('/v1/deliveries/<packId>', methods=['GET'])
def findDeliveryStatus(packId):
    response = " "
    try:
        robotId = deliveries[packId]
        for i in range(0, len(robots)):
            if (robots[i].idNum == robotId):
                response = robots[i].status
                break
        print("Robot could not be found")
    except KeyError:
        print("Package is unassigned or does not exist")
    return jsonify(response), 200


@app.route('/v1/robots', methods=['POST'])
def deliver():
    delivery = next(iter(deliveries.values()))

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5005, debug=True)

