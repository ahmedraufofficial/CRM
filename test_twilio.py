from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
account_sid = "AC8dc1c2e5a9c6c77d8d6d2e830f9c83bb"
auth_token = "bc7eb896a1c3f796280a126b9e249ede"

client = Client(account_sid, auth_token)

a = 971565256336
b = "+971549981998"
c = "not working"

print("Lesssgooo")
if(int(str(a)[:1]) == 9):
    print("First")
    a = "+"+str(a)
    print(a)
else:
    a = "+971"+str(a)
    print("Second")
    print(a)


#try:
#    message1 = client.messages.create(
  #  to=a,
 #   from_="+16073677078",
 #   body="Hello from Python!",
 #   )
#except TwilioRestException as err:
  #  print(c)
