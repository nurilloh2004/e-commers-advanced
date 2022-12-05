from api.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.utils import send_welcome_email, send_confirmation_email

@receiver(post_save, sender=Notification)
def sending_notification(sender, instance, created, **kwargs):
    if created:
       message = "Default Text"
       if instance.message:
      	      message = instance.message
       if instance.template:
              message = instance.template.message
       email = "shukurdev2002@gmail.com"
       
       print(email)
       try:
             send_welcome_email("shukurdev2002@gmail.com", message, ["shukurdev2002@gmail.com"])
       except:
             pass
       
 #message = 0
#        users = instance.user.all()
#        if instance.template:
#             message = instance.template
#        else:
#             message = instance.message
#        if message:
#              for user in users:
#                  send_welcome_email(user.email,message)
#
