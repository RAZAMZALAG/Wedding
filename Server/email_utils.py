import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Private information
SENDER_EMAIL = "shola.project.hadar@gmail.com"
SENDER_PASSWORD = "rzlo xsmn orxb atuk"

def send_email(to_email, subject, body):
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")


def send_verification_email(to_email, name, token):
    subject = "אימות כתובת הדוא\"ל שלך באתר Wedding Dreams"
    port = os.getenv("CLIENT_PORT")
    verification_link = f"http://localhost:{port}/api/auth/verify-email?token={token}"
    plain_text = f"""שלום {name} 👋

כמעט סיימנו!
כדי להשלים את ההרשמה לאתר Wedding Dreams ולאפשר לך להזמין מוצרי חתונה – נא לאמת את כתובת הדוא"ל שלך.

לחץ/י כאן לאימות:
{verification_link}

אם לא נרשמת לאתר – אפשר להתעלם מהמייל הזה.

תודה,
– צוות Wedding Dreams �
"""

    html_content = f"""
    <html dir="rtl" lang="he">
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>שלום {name} 👋</p>
        <p>כמעט סיימנו! כדי להשלים את ההרשמה לאתר Wedding Dreams ולאפשר לך להזמין מוצרי חתונה – נא לאמת את כתובת הדוא"ל שלך.</p>
        <p>
          <a href="{verification_link}" style="
            display: inline-block;
            padding: 10px 20px;
            background-color: #1e88e5;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
          ">
            לחץ/י כאן לאימות
          </a>
        </p>
        <p>אם לא נרשמת לאתר – אפשר להתעלם מהמייל הזה.</p>
        <p>תודה רבה �<br>צוות Wedding Dreams</p>
      </body>
    </html>
    """

    # בניית ההודעה
    message = MIMEMultipart("alternative")
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    # הוספת שתי הגרסאות – טקסט רגיל ו־HTML
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_content, "html"))

    # שליחה
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)
        server.quit()
        print(f"✅ Verification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send verification email to {to_email}: {e}")

def send_booking_pending_email(to_email, name, items, start_date, end_date):
    subject = "ההזמנה שלך לחתונה בבדיקה 💎"
    item_list = "\n".join([f"- {item}" for item in items])
    
    body = f"""שלום {name},

קיבלנו את הבקשה שלך להשכרת ציוד לחתונה, והיא כעת בבדיקה ✨  
הפריטים שביקשת:

{item_list}

🗓 תקופת השכרה: {start_date.strftime('%d/%m/%Y')} עד {end_date.strftime('%d/%m/%Y')}

נעדכן אותך ברגע שההזמנה תאושר ✉️

תודה שבחרת ב-Wedding Planner לחתונה שלך!  
– צוות Wedding Planner 💖
"""
    send_email(to_email, subject, body)

def send_booking_approved_email(to_email, name, items, total_price, order_date, event_date=None):
    subject = "ההזמנה שלך לחתונה אושרה! ✅"
    item_list = "\n".join([f"- {item}" for item in items])
    event_info = f"\n🎉 תאריך האירוע: {event_date.strftime('%Y-%m-%d')}" if event_date else ""
    
    body = f"""שלום {name} 👋

איזה כיף! ההזמנה שלך לחתונה אושרה 🎉

📦 פרטי ההזמנה:
{item_list}

🗓 תאריך ההזמנה: {order_date.strftime('%Y-%m-%d')}{event_info}

💰 סך הכול לתשלום: {total_price}₪

נצור איתך קשר לתיאום המסירה ופרטים נוספים 😊

מאחלים לכם חתונה מושלמת ובלתי נשכחת! �
– צוות Wedding Planner �
"""
    send_email(to_email, subject, body)

def send_return_reminder_email(to_email, name, return_date, item_names):
    subject = "📩 תזכורת להחזרת ציוד בקרוב"
    items_list = "\n".join(f"• {item}" for item in item_names)
    body = f"""שלום {name},

רק תזכורת קטנה 😊  
את/ה צפוי/ה להחזיר את המוצרים הבא עד לתאריך {return_date.strftime('%Y-%m-%d')}:

{items_list}

אם יש שאלה או קושי – אנחנו כאן. תודה על האחריות והשיתוף! �

– צוות Wedding Dreams
"""
    send_email(to_email, subject, body)

def send_return_thank_you_email(to_email, name):
    subject = "תודה על השירות 🙏 – נשמח לשמוע איך היה!"
    body = f"""שלום {name},

תודה שבחרת ב-Wedding Dreams לחתונה שלך �  
שיתוף הפעולה שלך מאפשר לנו להמשיך לספק שירות מעולה לכל הלקוחות שלנו.

נשמח לשמוע איך הייתה החוויה שלך:  
📋 מלא/י את טופס המשוב הקצר בלחיצה כאן:  
https://forms.gle/ZRr8bH1BFWrdsix47

המשוב שלך חשוב לנו מאוד!  
מקווים לראותך שוב ב-Wedding Dreams 😊

– צוות Wedding Dreams
"""
    send_email(to_email, subject, body)

def send_booking_rejected_email(to_email, name, items):
    subject = "ההזמנה שלך לא אושרה ❌"
    item_list = "\n".join([f"- {item}" for item in items])
    body = f"""שלום {name},

לצערנו, ההזמנה שביקשת דרך Wedding Dreams לא אושרה.  
הפריטים שביקשת היו:

{item_list}

אם יש שאלה או צורך בעזרה – אנחנו כאן בשבילך.  
מוזמן/ת לפנות אלינו בכל עת.

תודה שבחרת ב-Wedding Dreams �  
– צוות Wedding Dreams
"""
    send_email(to_email, subject, body)