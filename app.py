import urllib.request
import sqlite3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sched, time

con = sqlite3.connect('./gigs.db')

def search_key(fhand):
	nextline = False
	datetime = ""
	linkgig = ""
	gig_sql = "INSERT INTO gigs (dategig, linkgig) " \
			  "SELECT ?, ? " \
			  "WHERE NOT EXISTS(SELECT 1 FROM gigs WHERE dategig = ? AND linkgig = ?)"
	for line in fhand:
		words = line.decode()
		if nextline and (words.find("a href") > 0):
			linkgig = words.strip()
			cur = con.cursor()

			cur.execute(gig_sql, (datetime, linkgig, datetime, linkgig))
			con.commit()
			datetime = ""
			linkgig = ""
			nextline = False
		if words.find("time") > 0:
			posi = words.find("datetime")
			if posi > 0:
				posf = words.find(" title")
				datetime = words[posi + len("datetime") + 2:posf - 1]
				nextline = True


def send_emails():
	sender_email = "vladimirodriguez@gmail.com"
	receiver_email = "vladimirodriguez@gmail.com,mapsut@gmail.com,cloutymusic@gmail.com"
	port = 465  # For SSL
	password = "LcdNqeR_2019"

	context = ssl.create_default_context()

	message = MIMEMultipart("alternative")
	message["Subject"] = "Craigslist Work VR"
	message["From"] = sender_email
	message["To"] = receiver_email

	gig_sql = "SELECT * FROM GIGS WHERE GIG_SENT = false"

	cur = con.cursor()
	cur.execute(gig_sql)
	rows = cur.fetchall()
	updateStr = ""
	if len(rows) > 0:
		list = ""
		listHtml = ""
		for row in rows:
			posi = row[2].find("<a href=")
			posf = row[2].find("data")
			list += row[2][posi + len("<a href=") + 1:posf - 2] + "\n"
			listHtml += "<tr><td>" + row[1] + "</td><td>" + row[2] + "</td><tr>"
			if updateStr == "":
				updateStr = str(row[0])
			else:
				updateStr += ", " + str(row[0])

		gig_sql = "UPDATE GIGS SET GIG_SENT = true " \
					"WHERE id IN (" + updateStr + ")"
		cur = con.cursor()
		cur.execute(gig_sql)
		con.commit()
		print(list)

		# Create the plain-text and HTML version of your message
		text = """\
		Hi,
		How are you?
		These are the new gigs from craigslist: """ + list

		html = """\
		<html>
			<body>
			<p>Hi,<br>
			   How are you?<br> """ + listHtml + """has many great gigs.
			   </p>
			</body>
		</html>
		"""

		# Turn these into plain/html MIMEText objects
		part1 = MIMEText(text, "plain")
		part2 = MIMEText(html, "html")

		message.attach(part1)
		message.attach(part2)

		with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
			server.login("vladimirodriguez@gmail.com", password)
			server.sendmail(
				sender_email, receiver_email.split(','), message.as_string()
			)

def main_function(sc):
	key_words = ["mover", "truck", "couch", "driver", "delivery"]
	print("starting business")
	for key in key_words:

		handler = urllib.request.urlopen('https://newyork.craigslist.org/search/ggg?sort=date&is_paid=all&query=' + key)
		search_key(handler)
		send_emails()
	sc.enter(30, 1, main_function, (sc,))


if __name__ == "__main__":
	s = sched.scheduler(time.time, time.sleep)
	#main_function()

	s.enter(30, 1, main_function, (s,))
	s.run()
