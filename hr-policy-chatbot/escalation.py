import os 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime 
from dotenv import load_dotenv

load_dotenv()
SENDER_EMAIL        = os.getenv('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.getenv('SENDER_APP_PASSWORD')
HR_EMAIL            = os.getenv('HR_EMAIL')
CONFIDENCE_THRESHOLD = 50

def should_escalate(confidence: int) -> bool:
    return confidence < CONFIDENCE_THRESHOLD

def escalate_to_hr(employee_name: str, employee_id: str,
                   query: str, confidence: int) -> bool:
    if not all([SENDER_EMAIL, SENDER_APP_PASSWORD, HR_EMAIL]):
        print('Warning: Email credentials missing in .env')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'[HR Chatbot] Low Confidence Query — {employee_name}'
    msg['From']    = SENDER_EMAIL
    msg['To']      = HR_EMAIL

    plain_text = f"""
HR Policy Chatbot — Escalation Alert
=====================================
Employee Name  : {employee_name}
Employee ID    : {employee_id}
Query          : {query}
Confidence     : {confidence}%
Timestamp      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from the HR Policy Chatbot.
    """

    html_text = f"""
    <html><body style="font-family: Arial, sans-serif; color: #1C1C1C;">
      <h2 style="color:#1B4F72;">HR Policy Chatbot — Escalation Alert</h2>
      <p>An employee query received a
      <strong style="color:#E74C3C;">low confidence score
      ({confidence}%)</strong> and requires your attention.</p>
      <table style="border-collapse:collapse; width:100%; max-width:500px;">
        <tr style="background:#D6EAF8;">
          <td style="padding:8px 12px; border:1px solid #ccc;">
          <strong>Employee Name</strong></td>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          {employee_name}</td>
        </tr>
        <tr>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          <strong>Employee ID</strong></td>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          {employee_id}</td>
        </tr>
        <tr style="background:#D6EAF8;">
          <td style="padding:8px 12px; border:1px solid #ccc;">
          <strong>Query</strong></td>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          {query}</td>
        </tr>
        <tr>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          <strong>Confidence Score</strong></td>
          <td style="padding:8px 12px; border:1px solid #ccc;
          color:#E74C3C;">{confidence}%</td>
        </tr>
        <tr style="background:#D6EAF8;">
          <td style="padding:8px 12px; border:1px solid #ccc;">
          <strong>Timestamp</strong></td>
          <td style="padding:8px 12px; border:1px solid #ccc;">
          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
      </table>
      <p style="color:#777; font-size:13px; margin-top:20px;">
      This is an automated message from the HR Policy Chatbot.</p>
    </body></html>
    """

    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_text, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, HR_EMAIL, msg.as_string())
        print(f'Escalation email sent to {HR_EMAIL}')
        return True
    except Exception as e:
        print(f'Failed to send escalation email: {e}')
        return False
