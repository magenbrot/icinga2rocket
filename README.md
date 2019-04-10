# icinga2rocket

Python script to post Icinga2 notifications to your Rocket.Chat. It was tested with Icinga2, but it should work with little modifications on Icinga/Nagios, too.

## PREREQUISITES

Debian OS:
```
sudo apt install python3-requests
```

## CLONE THE REPO

Clone the repo to a folder on your Icinga2 host, e.g.:
```
git clone https://github.com/magenbrot/icinga2rocket.git
```

## SETUP Rocket.Chat

To connect this notification script with Rocket.Chat, you'll have to add an integration to your Rocket.Chat.

Go to Rocket.Chat Administration panel. Open the Integrations menu and create a new integration "incoming webhook".

Activate the Webhook, the following information is sufficient (examples):
 * Name: Icinga2Rocket
 * Channel: #monitoring

Remember the generated webhook URL for the next step.

You can use the "icinga-logo.png" in the images-folder for your app to easily identify messages
from Icinga2.


## SETUP ICINGA2

Add Icinga2 notification commands:
```
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
```

Add an Icinga2 Rocket.Chat user:
```
object User "rocket" {
        import "generic-user"

        # channel #monitoring:
        vars.rocket_url  = "<incoming_webhook_url>"
}
```

Add Icinga2 notification to hosts and services:
```
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
```

## TODO

+ error handling needed
