import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger_config import get_logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your-app-password')

logger = get_logger(__name__)

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
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)


def send_verification_email(to_email, name, token):
    subject = "אימות כתובת הדוא\"ל שלך באתר Wedding Dreams"
    # The verification link goes to the API server without redirect
    api_port = os.getenv("PORT", "5000")
    verification_link = f"http://localhost:{api_port}/api/auth/verify-email?token={token}"
    plain_text = f"""שלום {name} 👋

כמעט סיימנו!
כדי להשלים את ההרשמה לאתר Wedding Dreams ולאפשר לך להזמין מוצרי חתונה – נא לאמת את כתובת הדוא"ל שלך.

לחץ/י כאן לאימות:
{verification_link}

אם לא נרשמת לאתר – אפשר להתעלם מהמייל הזה.

תודה,
– צוות Wedding Dreams 💍
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
        logger.info(f"Verification email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}", exc_info=True)

def send_booking_pending_email(to_email, name, order_id, start_date, end_date, total_price):
    """Send booking pending confirmation email with MongoDB data"""
    from models import Order, Cart, Item
    
    subject = "ההזמנה שלך לחתונה בבדיקה 💎"
    
    try:
        # Get order details
        order = Order.find_by_id(order_id)
        if not order:
            logger.error(f"Order {order_id} not found for email")
            return
            
        # Get cart and items
        cart = Cart.find_by_id(order.cart_id)
        if not cart:
            logger.error(f"Cart {order.cart_id} not found for email")
            return
            
        # Build items list
        item_list = []
        for cart_item in cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                item_list.append(f"- {item.name} (כמות: {cart_item['amount']})")
        
        items_text = "\n".join(item_list) if item_list else "לא נמצאו פריטים"
        
        body = f"""שלום {name},

קיבלנו את הבקשה שלך להשכרת ציוד לחתונה, והיא כעת בבדיקה ✨

פרטי ההזמנה:
מספר הזמנה: {order_id}
תאריך האירוע: {start_date} עד {end_date}
סה"כ לתשלום: ₪{total_price}

הפריטים שהזמנת:
{items_text}

נבדוק את הזמינות ונחזור אליך בהקדם!

תודה,
צוות Wedding Dreams 💍"""

        send_email(to_email, subject, body)
        
    except Exception as e:
        logger.error(f"Error building pending email for order {order_id}: {str(e)}", exc_info=True)


def send_booking_approved_email(to_email, name, order_id, start_date, end_date):
    """Send booking approved email with MongoDB data"""
    from models import Order, Cart, Item
    
    subject = "ההזמנה שלך לחתונה אושרה! ✅"
    
    try:
        # Get order details
        order = Order.find_by_id(order_id)
        if not order:
            logger.error(f"Order {order_id} not found for email")
            return
            
        # Get cart and items
        cart = Cart.find_by_id(order.cart_id)
        if not cart:
            logger.error(f"Cart {order.cart_id} not found for email")
            return
            
        # Build items list
        item_list = []
        for cart_item in cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                item_list.append(f"- {item.name} (כמות: {cart_item['amount']})")
        
        items_text = "\n".join(item_list) if item_list else "לא נמצאו פריטים"
        
        body = f"""שלום {name},

מזל טוב! ההזמנה שלך לחתונה אושרה ✅

פרטי ההזמנה:
מספר הזמנה: {order_id}
תאריך האירוע: {start_date} עד {end_date}
סה"כ לתשלום: ₪{order.total_price}

הפריטים שאושרו:
{items_text}

נתראה ביום האירוע!

תודה,
צוות Wedding Dreams 💍"""

        send_email(to_email, subject, body)
        
    except Exception as e:
        logger.error(f"Error building approved email for order {order_id}: {str(e)}", exc_info=True)

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

def send_booking_rejected_email(to_email, name, order_id):
    """Send booking rejected email with MongoDB data"""
    from models import Order, Cart, Item
    
    subject = "ההזמנה שלך לא אושרה ❌"
    
    try:
        # Get order details
        order = Order.find_by_id(order_id)
        if not order:
            logger.error(f"Order {order_id} not found for email")
            return
            
        # Get cart and items
        cart = Cart.find_by_id(order.cart_id)
        if not cart:
            logger.error(f"Cart {order.cart_id} not found for email")
            return
            
        # Build items list
        item_list = []
        for cart_item in cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                item_list.append(f"- {item.name} (כמות: {cart_item['amount']})")
        
        items_text = "\n".join(item_list) if item_list else "לא נמצאו פריטים"
        
        body = f"""שלום {name},

לצערנו, ההזמנה שלך לא אושרה ❌

פרטי ההזמנה:
מספר הזמנה: {order_id}

הפריטים שנדחו:
{items_text}

אם יש שאלה או צורך בעזרה - אנחנו כאן בשבילך.

תודה,
צוות Wedding Dreams 💍"""

        send_email(to_email, subject, body)
        
    except Exception as e:
        logger.error(f"Error building rejected email for order {order_id}: {str(e)}", exc_info=True)