from bs4 import BeautifulSoup as bs
import urllib2
import re


class soFifaProfile:

	searchLink = 'https://sofifa.com/players?keyword='
	profileLink = 'https://sofifa.com/player/'

	def __init__(self,name):
		self.playerName = name.replace(' ','_')
		self.playerID = self.getPlayerID()
		self.profile = self.openPlayerPage()


	def getPlayerID(self):
		request = urllib2.Request(self.searchLink + self.playerName, headers = {'User-Agent' : 'Mozilla/5.0'})
		page = urllib2.urlopen(request)
		soup = bs(page.read(),'html5lib')
		searchResult = soup.select('a[href*="/player/"]')

		if(len(searchResult) != 1):
			raise SearchResultException('Player name brought up too many soFifa search results.')

		playerID = re.search(r'(?<=/)[0-9]+',str(searchResult[0])).group()

		return playerID


	def openPlayerPage(self):

		request = urllib2.Request(self.profileLink + self.playerID, headers = {'User-Agent' : 'Mozilla/5.0'})
                page = urllib2.urlopen(request)
                soup = bs(page.read(),'html5lib')
                return soup



        def getPosition(self):
		return str(self.profile.select('span[class*="pos pos"]')[0].contents[0])

	def getNation(self):
		listOfSpans = self.profile.select('span[class*="n"]')
		nationElement = listOfSpans[len(listOfSpans)-1] #For now, nation is the last element in this list. This is Google level stuff right here.
		return re.search(r'(?<=title\=\")[A-Za-z]+',str(nationElement)).group()

	def getClub(self):
		return str(self.profile.select('a[href*="/team/"]')[1].contents[0])

	def getRating(self):
		return str(self.profile.select('span[class*="label p"]')[0].contents[0])

	def getPotential(self):
		return str(self.profile.select('span[class*="label p"]')[1].contents[0])

class SearchResultException(Exception):
	pass
