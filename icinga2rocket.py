#!/usr/bin/env python3
"""

 Post Icinga2 notifications to Rocket.Chat channel by the incoming webhook feature

 Oliver Voelker <info@ovtec.it>

 Setup:

 Place this script in /usr/local/bin for example (please change the following
 command definition if you chose another location).

 Setup Rocket.Chat:

 To connect this notification script with Rocket.Chat, you'll have to add an integration to your Rocket.Chat.

 Go to Rocket.Chat Administration panel. Open the Integrations menu and create a new integration "incoming webhook".

 Activate the Webhook, the following information is sufficient (examples):
   * Name: Icinga2Rocket
   * Channel: #monitoring

 Remember the generated webhook URL for the next step.

 You can use the "icinga-logo.png" in the images-folder for your app to easily identify messages
 from Icinga2.


 Add Icinga2 notification commands:

 object NotificationCommand "rocket-host-notification" {
         command = [ "/usr/local/bin/icinga2rocket.py" ]

         arguments = {
                 "-u" = {
                         value = "$user.vars.rocket_url$"
                         required = true
                 }
                 "notificationtype" = {
                         value = "--field=NOTIFICATIONTYPE=$notification.type$"
                         skip_key = true
                 }
                 "hostalias" = {
                         value = "--field=HOSTALIAS=$host.name$"
                         skip_key = true
                 }
                 "hoststate" = {
                         value = "--field=HOSTSTATE=$host.state$"
                         skip_key = true
                 }
                 "hostoutput" = {
                         value = "--field=HOSTOUTPUT=$host.output$"
                         skip_key = true
                 }
         }
 }

 object NotificationCommand "rocket-service-notification" {
         command = [ "/usr/local/bin/icinga2rocket.py" ]

         arguments = {
                 "-u" = {
                         value = "$user.vars.rocket_url$"
                         required = true
                 }
                 "notificationtype" = {
                         value = "--field=NOTIFICATIONTYPE=$notification.type$"
                         skip_key = true
                 }
                 "hostalias" = {
                         value = "--field=HOSTALIAS=$host.name$"
                         skip_key = true
                 }
                 "servicedesc" = {
                         value = "--field=SERVICEDESC=$service.name$"
                         skip_key = true
                 }
                 "servicestate" = {
                         value = "--field=SERVICESTATE=$service.state$"
                         skip_key = true
                 }
                 "serviceoutput" = {
                         value = "--field=SERVICEOUTPUT=$service.output$"
                         skip_key = true
                 }
         }
 }

 Add an Icinga2 Rocket.Chat user:

 object User "rocket" {
         import "generic-user"

         # channel #monitoring:
         vars.rocket_url  = "<incoming_webhook_url>"
 }

 Add Icinga2 notifications to hosts and services:

 apply Notification "24x7-rocket-host-notification" to Host {
         import "rocket-host-notification"

         users = [ "rocket" ]

         vars.rocket_url = host.vars.rocket_url

         assign where host.vars.notifications == "24x7"
 }

 apply Notification "24x7-rocket-service-notification" to Service {
         import "rocket-service-notification"

         users = [ "rocket" ]

         vars.rocket_url = service.vars.rocket_url

         assign where host.vars.notifications == "24x7"
         ignore where match("*ssl-cert*",service.name)
         ignore where service.name == "backup_diskspace"
 }


 You can simply add more Rocket.Chat instances (for example of your customers) and apply
 notifications for their hosts and services.

"""

from __future__ import print_function
import sys

try:
    import optparse
    import requests

except ImportError as error:
    print("Missing python module: {}".format(error.message))
    sys.exit(255)

def main():
    """ Main function """

    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', dest="url", action="store", help="The URL of the incoming webhook generated in the Rocket.Chat administration")
    parser.add_option('-f', '--field', dest="field", action="append", help="Those fields get filled in by Icinga2")
    options, args = parser.parse_args()

    if not options.url or not options.field:
        #parser.error("Argument missing")
        parser.print_help()
        sys.exit(1)

    headers = {'Content-type': 'application/json'}
    msg_dict = {k:v for k,v in (x.split('=', 1) for x in options.field) }

    # debug
    #for key,value in msg_dict.items():
    #    print(key,value)

    message = msg_dict["NOTIFICATIONTYPE"] + ": " + msg_dict["HOSTALIAS"]
    if "SERVICEDESC" in msg_dict:
        message += " / " + msg_dict["SERVICEDESC"] + " is " + msg_dict["SERVICESTATE"] + ":\n" + msg_dict["SERVICEOUTPUT"]
    elif "HOSTSTATE" in msg_dict:
        message += " is " + msg_dict["HOSTSTATE"] + ":\n" + msg_dict["HOSTOUTPUT"]

    payload = {'text': message + '\n'}
    print(payload)
    r = requests.post(options.url, json=payload, headers=headers)
    
    if r.status_code != 200:
        raise ValueError('Request to Rocket.Chat returned an error %s, the response is:\n%s' % (r.status_code, r.text))

#
# Begin
#

if __name__ == "__main__":
    main()
