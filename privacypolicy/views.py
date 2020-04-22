from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .apps import WebappConfig

class call_model(APIView):

	def __init__(self):
		self.scrapperRef = WebappConfig.scrapper
		self.vectorizeRef = WebappConfig.vectorizer
		self.filterRef = WebappConfig.filterer
		self.tokenizerRef = WebappConfig.tokenizer
		self.graderRef = WebappConfig.grader

	def scraperFun(self, weblink):
		pageContent = self.scrapperRef(weblink)
		return pageContent

	def vectorizeFun(self, pageContent):
		type1Data = self.vectorizeRef("type1", pageContent)
		type2Data = self.vectorizeRef("type2", pageContent)
		type3Data = self.vectorizeRef("type3", pageContent)
		type4Data = self.vectorizeRef("type4", pageContent)
		type5Data = self.vectorizeRef("type5", pageContent)
		type6Data = self.vectorizeRef("type6", pageContent)
		return [type1Data, type2Data, type3Data, type4Data, type5Data, type6Data]

	def filterFun(self, pageContent, vectorizedData):
		type1Filtered = self.filterRef(vectorizedData[0], pageContent, "type1")
		type2Filtered = self.filterRef(vectorizedData[1], pageContent, "type2")
		type3Filtered = self.filterRef(vectorizedData[2], pageContent, "type3")
		type4Filtered = self.filterRef(vectorizedData[3], pageContent, "type4")
		type5Filtered = self.filterRef(vectorizedData[4], pageContent, "type5")
		type6Filtered = self.filterRef(vectorizedData[5], pageContent, "type6")
		return [type1Filtered, type2Filtered, type3Filtered, type4Filtered, type5Filtered, type6Filtered]

	def tokenizeFun(self, filteredData):
		type1Padded = self.tokenizerRef(filteredData[0], "type1")
		type2Padded = self.tokenizerRef(filteredData[1], "type2")
		type3Padded = self.tokenizerRef(filteredData[2], "type3")
		type4Padded = self.tokenizerRef(filteredData[3], "type4")
		type5Padded = self.tokenizerRef(filteredData[4], "type5")
		type6Padded = self.tokenizerRef(filteredData[5], "type6")
		return [type1Padded, type2Padded, type3Padded, type4Padded, type5Padded, type6Padded]

	def gradeFun(self, paddedData):

		if len(paddedData[0]) < 10:
			if len(paddedData[0]) < 5:
				type1Grade = [0, 0, len(paddedData[0])]
			else:
				type1Grade = type1Grade = [0, len(paddedData[0]), 0]
		else:
			type1Grade = self.graderRef(paddedData[0], "type1")

		if len(paddedData[1]) < 10:
			if len(paddedData[1]) < 5:
				type2Grade = [0, 0, len(paddedData[1])]
			else:
				type2Grade = [0, len(paddedData[1]), 0]
		else:
			type2Grade = self.graderRef(paddedData[1], "type2")

		if len(paddedData[2]) < 2:
			if len(paddedData[2]) < 1:
				type3Grade = [0, 0, len(paddedData[2])]
			else:
				type3Grade = [0, len(paddedData[2]), 0]
		else:
			type3Grade = self.graderRef(paddedData[2], "type3")

		if len(paddedData[3]) < 10:
			if len(paddedData[3]) < 5:
				type4Grade = [0, 0, len(paddedData[3])]
			else:
				type4Grade = [0, len(paddedData[3]), 0]
		else:
			type4Grade = self.graderRef(paddedData[3], "type4")

		if len(paddedData[4]) < 1:
			type5Grade = [0, 0, len(paddedData[4])]
		else:
			type5Grade = self.graderRef(paddedData[4], "type5")

		if len(paddedData[5]) < 1:
			type6Grade = [0, 0, len(paddedData[5])]
		else:
			type6Grade = self.graderRef(paddedData[5], "type6")
		
		return [type1Grade, type2Grade, type3Grade, type4Grade, type5Grade, type6Grade]

	def calculateScore(self, gradedData):
		scores = []
		color = []
		low = 8.32
		mid = 4.99
		high = 1.66

		for i in range(len(gradedData)):
			sentenceNum = gradedData[i][0] + gradedData[i][1] + gradedData[i][2]
			if sentenceNum == 0:
				scores.append(0)
				color.append('#39ff14')
			else:
				catScore = low * gradedData[i][0] + mid * gradedData[i][1] + high * gradedData[i][2]
				catScore = int(catScore / sentenceNum * 10)
				scores.append(catScore)
				if catScore < 34:
					color.append('#ff1439')
				elif catScore < 67:
					color.append('#1439ff')
				else:
					color.append('#39ff14')

		return [scores, color]

	def post(self, request):
		# Fetch Link from GUI in string(weblink)
		weblink = JSONParser().parse(request)["weblink"]

		# Scrape Webpage using Scrapper Ref, check for errors
		pageContent = self.scraperFun(weblink)
		pageSize = len(pageContent)
		if pageSize < 10:
			# Handle Scrapping Unsuccessful here in this if block!! The below statement is temporary
			print("Scrapping Failure v.1")
			# return render(request, "output.html", {'pageContent' : pageSize})
			return JsonResponse({}, status = 400)
		print("Scraped Successfully")

		# Vectorize the pageContent if pipeline proceeds
		vectorizedData = self.vectorizeFun(pageContent)
		# print(vectorizedData[0].shape, "\n", vectorizedData[1].shape, "\n", vectorizedData[2].shape, "\n", vectorizedData[3].shape, "\n", vectorizedData[4].shape, "\n", vectorizedData[5].shape, "\n")
		print("Vectorized Successfully")

		# Filter the vectorized Data
		filteredData = self.filterFun(pageContent, vectorizedData)
		# print(filteredData[0].shape, "\n", filteredData[1].shape, "\n", filteredData[2].shape, "\n", filteredData[3].shape, "\n", filteredData[4].shape, "\n", filteredData[5].shape, "\n")
		print("Filtered Successfully")

		# Check for scrape v.2
		totalData = 0
		for i in range(0, 5):
			totalData = totalData + len(filteredData[i])
		if totalData < 6:
			print("Scrapping Failure v.2")
			# return render(request, "output.html", {'pageContent' : pageSize})
			return JsonResponse({}, status = 400)

		# Tokenize the filtered Data, Prepare for Grading 
		paddedData = self.tokenizeFun(filteredData)
		# print(paddedData[0].shape, "\n", paddedData[1].shape, "\n", paddedData[2].shape, "\n", paddedData[3].shape, "\n", paddedData[4].shape, "\n", paddedData[5].shape, "\n")
		print("Tokenized Successfully")

		# Grade the Data
		gradedData = self.gradeFun(paddedData)
		# print(gradedData[0], "\n", gradedData[1], "\n", gradedData[2], "\n", gradedData[3], "\n", gradedData[4], "\n", gradedData[5], "\n")
		print("Graded Successfully")

		# Calculate final scores
		finalOutput = self.calculateScore(gradedData)
		finalScores = finalOutput[0]
		finalColor = finalOutput[1]
		# print(finalScores)
		print("All Done!!!!")
		
		return JsonResponse({"Type1" : finalScores[0], "Type2" : finalScores[1], "Type3" : finalScores[2], "Type4" : finalScores[3], "Type5" : finalScores[4], "Type6" : finalScores[5]}, status = 201)