#def insert_list_of_titles_into_mysql():
#	import requests
#	from bs4 import BeautifulSoup as bs
#	file_="/home/david/Desktop/Programming/etc..."
#	file_handler = open(file_,'r')
#	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
 #                    user="",         # your username
  #                   passwd="",  # your password
   #                  db="imdb_stuff")        #
#	cursor = db.cursor()
#	for line in file_handler:
#		print line
#		data=line.split("\t")
#		data[0]
#		query="INSERT INTO movie_list (Movie,average,total_count,0,1,2,3,4,5,6,7,8,9,10) values ("+ data[3] + "," + data[2] + "," + data[1] + "," + data[0][0] + "," + data[0][1] + "," + data[0][2] +"," + data[0][3] + "," + data[0][4] + "," + data[0][5] + "," + data[0][6] + "," + data[0][7] + "," + data[0][8] + "," + data[0][9] + ");"
#		print query
#		cursor.execute(query)
#	return True


#The above code was originally going to put data from a downloadable IMDB file into a database.
#I later decided that it was useless, but I wanted to save the code for later in case I do find a use for it.


def grab_top_rated_titles(total_entries):
	import requests
	from bs4 import BeautifulSoup as bs
	import time
	import random
	import MySQLdb
	entry_number=1
	headers={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
	while (entry_number<total_entries):
		r=requests.get("http://www.imdb.com/search/title?groups=top_2000&sort=num_votes&view=simple&start="+str(entry_number),headers=headers)
		time.sleep(4+6*random.random())
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="imdb_stuff")        #
		cursor = db.cursor()
		soup=bs(r._content,'html.parser')
		data_table=soup.find_all('td',class_="title")
		for i in data_table:
			title=i.parent.find("td",class_="title").contents[0].contents[0]
			tag=i.parent.find("a")['href'][7:-1]
			vote_count=i.parent.find_all("td")[3].contents[0].strip().replace(",","")
			query="INSERT INTO top_titles (id,title,vote_count) values (\"" + str(tag) + "\",\"" + title + "\"," + str(vote_count) + ");"
			print query
			cursor.execute(query)
		db.commit()
		db.close()
		entry_number+=100
		print "\n\n"
	return True


def scan_gender_disparities(max_vote=99999999):
	import requests
	from bs4 import BeautifulSoup as bs
	import time
	import random
	import MySQLdb
	import math
	headers={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
	male_votes=[0,0,0,0,0,0,0,0,0,0,0]
	male_perc=[0,0,0,0,0,0,0,0,0,0,0]
	female_votes=[0,0,0,0,0,0,0,0,0,0,0]
	female_perc=[0,0,0,0,0,0,0,0,0,0,0]
	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="imdb_stuff")        #
	db2 = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="imdb_stuff")
	cursor = db.cursor()
	cursor2 = db2.cursor()
	query="SELECT id, title, vote_count from top_titles WHERE vote_count<" + str(max_vote) + " ORDER BY vote_count DESC;"
	cursor.execute(query)
	while(cursor.rownumber<cursor.rowcount):
		info=cursor.fetchone()
		try:
			print str(info)+" "+str(cursor.rownumber)+"/"+str(cursor.rowcount)
		except UnicodeDecodeError:
			print "Unicode error"
		ttid=info[0]
		title=info[1]
		total_vote_count=info[2]
		r=requests.get("http://www.imdb.com/title/" + ttid + "/ratings-male",headers=headers)
		soup=bs(r._content,'html.parser')
		year=soup.find_all("a",class_="main")[0].parent.find_all("a")[1].contents[0]
		for j in range(0,10):
			rating=int(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].next_sibling.contents[0])
			vote_count=int(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].previous_sibling.contents[0])
			percentage=float(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].contents[0].contents[0].strip()[:-1])
			male_votes[rating]=vote_count
			male_perc[rating]=percentage
		time.sleep(4*random.random())
		r=requests.get("http://www.imdb.com/title/" + ttid + "/ratings-female",headers=headers)
		time.sleep(4*random.random())
		soup=bs(r._content,'html.parser')
		for j in range(0,10):
			rating=int(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].next_sibling.contents[0])
			vote_count=int(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].previous_sibling.contents[0])
			percentage=float(soup.find_all('td',background="http://i.media-imdb.com/images/rating/ruler.gif")[j].contents[0].contents[0].strip()[:-1])
			female_votes[rating]=vote_count
			female_perc[rating]=percentage
		male_avg=0
		total_male_votes=0
		female_avg=0
		total_female_votes=0
		for j in range(1,11):
			male_avg+=j*male_votes[j]
			total_male_votes+=male_votes[j]
			female_avg+=j*female_votes[j]
			total_female_votes+=female_votes[j]
		male_avg/=float(total_male_votes)
		female_avg/=float(total_female_votes)
		male_variance=0
		female_variance=0
		for j in range(1,11):
			male_variance+=male_votes[j]*math.pow((j-male_avg),2)
			female_variance+=female_votes[j]*math.pow((j-female_avg),2)
		male_variance/=float(total_male_votes)
		female_variance/=float(total_female_votes)			
		try:
			query="INSERT INTO gender_ratings (id, title, year, " + "male_one_vote_count, male_one_vote_perc, " + "male_two_vote_count, male_two_vote_perc, " + "male_three_vote_count, male_three_vote_perc," + "male_four_vote_count, male_four_vote_perc, " + "male_five_vote_count, male_five_vote_perc, " + "male_six_vote_count, male_six_vote_perc, " + "male_seven_vote_count, male_seven_vote_perc," + "male_eight_vote_count, male_eight_vote_perc, " + "male_nine_vote_count, male_nine_vote_perc, " + "male_ten_vote_count, male_ten_vote_perc," + "male_average, male_variance," + "female_one_vote_count, female_one_vote_perc," + "female_two_vote_count, female_two_vote_perc, " + "female_three_vote_count, female_three_vote_perc," + "female_four_vote_count, female_four_vote_perc, " + "female_five_vote_count, female_five_vote_perc, " + "female_six_vote_count, female_six_vote_perc, " + "female_seven_vote_count, female_seven_vote_perc, " + "female_eight_vote_count, female_eight_vote_perc, " + "female_nine_vote_count, female_nine_vote_perc, " + "female_ten_vote_count, female_ten_vote_perc," + "female_average, female_variance," + "one_vote_gender_difference," + "ten_vote_gender_difference," + "average_gender_difference," + "variance_gender_difference" + ") values (\"" + ttid + "\", \"" + title + "\", " + year + ", " + str(male_votes[1]) + ", " + str(male_perc[1])  + ", " + str(male_votes[2]) + ", " + str(male_perc[2])  + ", " + str(male_votes[3]) + ", " + str(male_perc[3])  + ", " + str(male_votes[4]) + ", " + str(male_perc[4])  + ", " + str(male_votes[5]) + ", " + str(male_perc[5])  + ", " + str(male_votes[6]) + ", " + str(male_perc[6])  + ", " + str(male_votes[7]) + ", " + str(male_perc[7])  + ", " + str(male_votes[8]) + ", " + str(male_perc[8])  + ", " + str(male_votes[9]) + ", " + str(male_perc[9])  + ", " + str(male_votes[10]) + ", " + str(male_perc[10])  + ", " +  str(male_avg) + ", " + str(male_variance) + ", " + str(female_votes[1]) + ", " + str(female_perc[1])  + ", " + str(female_votes[2]) + ", " + str(female_perc[2])  + ", " + str(female_votes[3]) + ", " + str(female_perc[3])  + ", " + str(female_votes[4]) + ", " + str(female_perc[4])  + ", " + str(female_votes[5]) + ", " + str(female_perc[5])  + ", " + str(female_votes[6]) + ", " + str(female_perc[6])  + ", " + str(female_votes[7]) + ", " + str(female_perc[7])  + ", " + str(female_votes[8]) + ", " + str(female_perc[8])  + ", " + str(female_votes[9]) + ", " + str(female_perc[9])  + ", " + str(female_votes[10]) + ", " + str(female_perc[10])  + ", " +  str(female_avg) + ", " + str(female_variance) + ", " +str(male_perc[1]-female_perc[1]) + ", " +str(male_perc[10]-female_perc[10]) + ", " +str(male_avg-female_avg)  + ", " + str(male_variance-female_variance)  + ");" 
			#print query + "\n\n"
			cursor2.execute(query)
			db2.commit()
		except UnicodeDecodeError:
			print "Unicode error" 
	db.close()
	db2.close()
	return True


if __name__ == "__main__":
	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="")
	cursor=db.cursor()
	query1="CREATE DATABASE imdb_stuff;"
	query2="create table top_titles (auto_id int(10) unsigned not null primary key auto_increment, id varchar(9) not null, title varchar(50) not null, vote_count int(10) not null);"
	query3="create table gender_ratings (auto_id int(10) unsigned not null primary key auto_increment, id varchar(9) not null, title varchar(50) not null, year int(4),male_one_vote_count int(10), male_one_vote_perc float(4,2) not null,male_two_vote_count int(10), male_two_vote_perc float(4,2) not null, male_three_vote_count int(10), male_three_vote_perc float(4,2) not null, male_four_vote_count int(10), male_four_vote_perc float(4,2) not null, male_five_vote_count int(10), male_five_vote_perc float(4,2) not null, male_six_vote_count int(10), male_six_vote_perc float(4,2) not null, male_seven_vote_count int(10), male_seven_vote_perc float(4,2) not null, male_eight_vote_count int(10), male_eight_vote_perc float(4,2) not null, male_nine_vote_count int(10), male_nine_vote_perc float(4,2) not null, male_ten_vote_count int(10), male_ten_vote_perc float(4,2) not null,male_average float(4,2) not null, male_variance float(4,2) not null,female_one_vote_count int(10), female_one_vote_perc float(4,2) not null,female_two_vote_count int(10), female_two_vote_perc float(4,2) not null, female_three_vote_count int(10), female_three_vote_perc float(4,2) not null, female_four_vote_count int(10), female_four_vote_perc float(4,2) not null, female_five_vote_count int(10), female_five_vote_perc float(4,2) not null, female_six_vote_count int(10), female_six_vote_perc float(4,2) not null, female_seven_vote_count int(10), female_seven_vote_perc float(4,2) not null, female_eight_vote_count int(10), female_eight_vote_perc float(4,2) not null, female_nine_vote_count int(10), female_nine_vote_perc float(4,2) not null, female_ten_vote_count int(10), female_ten_vote_perc float(4,2) not null,female_average float(4,2) not null, female_variance float(4,2) not null,one_vote_gender_difference float(4,2) not null,ten_vote_gender_difference float(4,2) not null,average_gender_difference float(4,2) not null,variance_gender_difference float(4,2) not null);"
	grab_top_rated_titles(6000)
	scan_gender_disparities()
