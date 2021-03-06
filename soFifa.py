from bs4 import BeautifulSoup as bs
import urllib2
import re
import json
from unidecode import unidecode

class SearchResultException(Exception):
	pass

class Profile:

	searchLink = 'https://sofifa.com/players?keyword='
	profileLink = 'https://sofifa.com/player/'

	def __init__(self,name,playerID=None):
		self.playerName = name.replace(' ','_')
		self.playerID = self.getPlayerID(playerID)
		self.profile = self.openPlayerPage()

		playerName = self.profile.find('div',class_='meta').find('span').contents[0]
		Nation = str(self.profile.find('div',class_='meta').find('span').contents[1]['title'])
		Age = int(re.search(r'(?<=Age )[0-9]+' , self.profile.find('div',class_='meta').find('span').contents[-1]).group())
		Positions = [span.contents[0] for span in self.profile.find('div',class_='meta').span.find_all('span')]
		Club = unicode(self.profile.find_all('a',href= re.compile('/team/[0-9]+'))[0].contents[0])
		Rating = int(self.profile.find_all('td',class_='text-center')[0].find('span').contents[0])
		Potential = int(self.profile.find_all('td',class_='text-center')[1].find('span').contents[0])

		self.json = {
		'Name' : playerName,
		'ID' : playerID ,
		'Age' : Age ,
		'Nation' : Nation ,
		'Club' : Club ,
		'Positions' : Positions ,
		'Rating' : Rating ,
		'Potential' : Potential
		}

#						CONSTRUCTOR HELPER METHODS
#-------------------------------------------------------------------------------

	def getPlayerID(self,playerIDFromUser):
		if(playerIDFromUser != None):
			return str(playerIDFromUser)

		request = urllib2.Request(self.searchLink + self.playerName, headers = {'User-Agent' : 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		html = bs(page.read(),'html5lib')
		searchResult = html.select('a[href*="/player/"]')

		if(len(searchResult) != 1):
			raise SearchResultException('Player name brought up too many soFifa search results, so playerID couldn\'t be retrieved. Please provide a playerID.')

		playerID = re.search(r'(?<=/)[0-9]+',str(searchResult[0])).group()

		return playerID

	def openPlayerPage(self):

		request = urllib2.Request(self.profileLink + self.playerID, headers = {'User-Agent' : 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		html = bs(page.read(),'html5lib')
		return html

#							GETTERS START HERE
#-------------------------------------------------------------------------------

	def getName(self):
		return self.json["Name"]

	def getNation(self):
		return self.json["Nation"]

	def getPositions(self):
		return self.json["Positions"]

	def getClub(self):
		return self.json["Club"]

	def getRating(self):
		return self.json["Rating"]

	def getPotential(self):
		return self.json["Potential"]

	def getAge(self):
		return self.json["Age"]

	def __str__(self):
		return str(self.json)

class Squad:

	teamIDs = json.load(open('TeamDictionary.json'))
	teamLink = 'https://sofifa.com/team/'


	def __init__(self,team):
		self.teamID = self.teamIDs[team]
		self.teamLink += str(self.teamID)

	def report(self):
		request = urllib2.Request(self.teamLink, headers={'User-Agent': 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		html = bs(page.read(), 'html5lib')

		mainSquadTable = html.find_all('table', class_="table table-hover persist-area")[0].tbody
		loaneeTable = html.find_all('table', class_="table table-hover persist-area")[1].tbody
		teamName = re.search(r'[A-Za-z ]+',str(html.find('div', class_="info").h1.contents[0])).group().strip()

		mainRows = mainSquadTable.find_all('tr')
		loaneeRows = loaneeTable.find_all('tr')

		response = {"teamName": teamName, "players": []}

		self.loadPlayers(mainRows,False,response["players"])
		self.loadPlayers(loaneeRows,True,response["players"])

		return response

	def loadPlayers(self,rows,loaned,playerList):
		for i in range(len(rows)):

			row = rows[i].find_all('td')
			infoCell = row[1].div.find_all('a')
			nation = re.search(r'(?<=title\=\")[A-Za-z ]+', str(infoCell[0])).group()
			name = ""
			try:
				name = unidecode(unicode((re.search(r'(?<=title\=\")[^\"]+', str(infoCell[1])).group())))
			except Exception as e:
				print 'Failed on ' + str(infoCell), str(e)
			position = str(infoCell[2].span.contents[0])
			age = str(row[2].div.contents[0]).replace('\n', '')
			rating = int(row[3].div.span.contents[0])
			potential = int(row[4].div.span.contents[0])
			growth = potential - rating
			if(loaned):
				loanedTo = row[5].a.contents[0]
			else:
				loanedTo = None

			playerList.append(
				{"Age": age, "Name": name, "Position": position, 'Nation': nation, "Rating": rating,
				 "Potential": potential,
				 "Growth": growth, "Loaned": loaned, "LoanedTo": loanedTo})
