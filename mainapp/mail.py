import os

from mailjet_rest import Client
from dotenv import load_dotenv, find_dotenv

class mail:
    def __init__(self) -> None:
        load_dotenv(find_dotenv())
        self.api_key = os.environ.get('API_KEY')
        self.api_secret = os.environ.get('API_SECRET')
        self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        print('here loaded mail module')

    def mail_2_customer(self, name, mail, message, ticket):
        data = {
            'Messages': [
                {
                "From": {
                    "Email": "einstienthegreatscientist@gmail.com",
                    "Name": "Ashutosh"
                },
                "To": [
                        {
                            "Email": mail,
                            "Name": name
                        }
                    ],
                    "Subject": "Haze Busters Support Team",

                    "TextPart": f"""Hey {name}! I hope this message finds you well. We wanted to reach out and express our gratitude for taking the time to fill out our Contact Us form. Your feedback and inquiries are important to us, and we appreciate your interest in our products/services. We have received your message, and your query is sent to our customer support team. Please allow us some time to carefully review the information you provided, and we will get back to you as soon as possible. <br> <br> Here are the details you provided during your contact form submission: Ticket Number: {ticket}, Name: {name},Email: {mail}, Message: {message}. In the meantime, if you have any additional information or specific details you'd like to share, please feel free to reply to this email. The more information we have, the better we can assist you. Best regards, Team Haze Busters: ashutosh.patel2021@vitbhopal.ac.in """,

                    "HTMLPart": f"""<link rel="preconnect" href="https://fonts.googleapis.com"> <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch&family=Poppins:wght@300;400&display=swap" rel="stylesheet"> <div style="background: #eaeaea; display: flex;"> <div style="background: #fff; padding: 1rem 2rem; width: 60%; margin: auto;"> <h1 style="font-family:'Chakra Petch'; font-size: 2rem; line-height: 3rem ;text-align:center">Haze Busters</h1> <p style="font-family:'Poppins'; font-size: 1rem;"> Hey {name}! <br> I hope this message finds you well. We wanted to reach out and express our gratitude for taking the time to fill out our Contact Us form. Your feedback and inquiries are important to us, and we appreciate your interest in our products/services. <br> <br> We have received your message, and your query is sent to our customer support team. Please allow us some time to carefully review the information you provided, and we will get back to you as soon as possible. <br> <br> Here are the details you provided during your contact form submission: </p> <br> <br> <div style="width: max-content; margin: auto; font-size: 1rem; padding: 0.75rem 1rem; line-height: 1.25rem; border: 1px solid black; border-radius: 10px;"> <code>Ticket Number: {ticket}<br>Name: {name}<br>Email: {mail}<br>Message: {message}</code> </div> <br> <br> <p style="font-family:'Poppins'; font-size: 1rem;"> In the meantime, if you have any additional information or specific details you'd like to share, please feel free to reply to this email. The more information we have, the better we can assist you. <br> <br> Best regards,<br>Team Haze Busters<br>ashutosh.patel2021@vitbhopal.ac.in </p> </div> </div>"""
                }
            ]
        }
        return data
    
    def mail_2_dev(self, name, mail, message, ticket):
        data = {
            'Messages': [
                {
                "From": {
                    "Email": "einstienthegreatscientist@gmail.com",
                    "Name": "Ashutosh"
                },
                "To": [
                        {
                            "Email": "einstienthegreatscientist@gmail.com",
                            "Name": "Ashutosh"
                        }
                    ],
                    "Subject": "Haze Busters Support Team",

                    "TextPart": f"""Ticket Number: {ticket}, Hey Developer!. A new contact form submission has been received from a user. Here are the details provided:Ticket Number: {ticket}, Name: {name}, Email: {mail}, Message: {message}. Please take the following steps to address this submission: 1.Review the user's message. 2.Assess the nature of the inquiry or feedback. 3. Respond to the user's query or request in a timely manner.""",

                    "HTMLPart": f"""<link rel="preconnect" href="https://fonts.googleapis.com"> <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch&family=Poppins:wght@300;400&display=swap" rel="stylesheet"><div style="background: #eaeaea; display: flex;"> <div style="background: #fff; padding: 1rem; width: 60%; margin: auto;"> <h1 style="font-family:'Chakra Petch'; font-size: 3rem; line-height: 3rem ;text-align:center">Ticket Number: {ticket}</h1> <p style="font-size: 1.5rem; font-family: 'Poppins';"> Hey Developer! <br> A new contact form submission has been received from a user. Here are the details provided: </p> <br> <br> <div style="width: max-content; margin: auto; font-size: 1.5rem; padding: 0.75rem 1rem; line-height: 2.5rem; border: 1px solid black; border-radius: 10px;"> <code>Ticket Number: {ticket} <br>Name: {name} <br>Email: {mail} <br>Message: {message} </code> </div> <br> <br> <p style="font-size: 1.5rem; font-family: 'Poppins';"> Please take the following steps to address this submission: <ol> <li style="font-size: 1.5rem; font-family: 'Poppins';">Review the user's message.</li> <li style="font-size: 1.5rem; font-family: 'Poppins';">Assess the nature of the inquiry or feedback.</li> <li style="font-size: 1.5rem; font-family: 'Poppins';">Respond to the user's query or request in a timely manner.</li> </ol> </p> </div> </div>"""
                }
            ]
        }
        return data
    
    def send_mail(self, name, mail, message, ticket):
        data = self.mail_2_customer(name, mail, message, ticket)
        result = self.mailjet.send.create(data=data)

        data = self.mail_2_dev(name, mail, message, ticket)
        result = self.mailjet.send.create(data=data)

        return "Success"

# if __name__ == "__main__":
#     name = 'Ashutosh'
#     mail_id = 'shreyas27patondikar@gmail.com'
#     message = 'hi'
#     ticket = '765348631'

#     issue = mail()
#     issue.send_mail(name, mail_id, message, ticket)

