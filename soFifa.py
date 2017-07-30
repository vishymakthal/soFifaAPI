from bs4 import BeautifulSoup as bs
import urllib2
import re

class SearchResultException(Exception):
	pass

class soFifaProfile:

	searchLink = 'https://sofifa.com/players?keyword='
	profileLink = 'https://sofifa.com/player/'

	def __init__(self,name,playerID=None):
		self.playerName = name.replace(' ','_')
		self.playerID = self.getPlayerID(playerID)
		self.profile = self.openPlayerPage()

		self.Nation = str(re.search(r'(?<=title\=\")[A-Za-z ]+' , str(self.profile.find('div',class_='meta').find('span').contents[1])).group())
		self.Age = int(re.search(r'(?<=Age )[0-9]+' , self.profile.find('div',class_='meta').find('span').contents[-1]).group())
		self.Position = str(self.profile.find('div',class_='meta').find('span').find_all('span')[1].contents[0])
		self.Club = str(self.profile.find_all('a',href= re.compile('/team/[0-9]+'))[0].contents[0])
		self.Rating = int(self.profile.find_all('td',class_='text-center')[0].find('span').contents[0])
		self.Potential = int(self.profile.find_all('td',class_='text-center')[1].find('span').contents[0])

		self.json = {
		'Name' : name,
		'ID' : self.playerID ,
		'Age' : self.Age ,
		'Nation' : self.Nation ,
		'Club' : self.Club ,
		'Position' : self.Position ,
		'Rating' : self.Rating ,
		'Potential' : self.Potential
		}


#						CONSTRUCTOR HELPER METHODS
#-------------------------------------------------------------------------------

	def getPlayerID(self,playerIDFromUser):
		if(playerIDFromUser != None):
			return playerIDFromUser

		request = urllib2.Request(self.searchLink + self.playerName, headers = {'User-Agent' : 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		soup = bs(page.read(),'html5lib')
		searchResult = soup.select('a[href*="/player/"]')

		if(len(searchResult) != 1):
			raise SearchResultException('Player name brought up too many soFifa search results, so playerID couldn\'t be retrieved. Please provide a playerID.')

		playerID = re.search(r'(?<=/)[0-9]+',str(searchResult[0])).group()

		return playerID

	def openPlayerPage(self):

		request = urllib2.Request(self.profileLink + self.playerID, headers = {'User-Agent' : 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		soup = bs(page.read(),'html5lib')
		return soup

#							GETTERS START HERE
#-------------------------------------------------------------------------------

	def getNation(self):
		return self.Nation

	def getPosition(self):
		return self.Position

	def getClub(self):
		return self.Club

	def getRating(self):
		return self.Rating

	def getPotential(self):
		return self.Potential

	def getAge(self):
		return self.Age

	def __str__(self):
		return str(self.json)
