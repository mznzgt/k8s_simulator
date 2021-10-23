import threading
import time
import math
#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.
#apiServer is the apiServer
#running is the running status of the HPA
#time is the checking period for the algorithm
#deploymentLabel is the label of the associated deployment
#setPoint is the setpoint for cpu utilisation
#maxReps is the max number of pod replicas
#minReps is the minimum number of pod replicas

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
		#self.deploymentLabel = INFOLIST[0]
		self.microserviceLabel = INFOLIST[0]
		self.setPoint = float(INFOLIST[1])/100
		self.maxReps = 5
		self.minReps = 1
	def __call__(self):
		while self.running:
			with self.apiServer.etcdLock:
				#deployment = self.apiServer.GetDepByLabel(self.deploymentLabel)
				#microservice = self.apiServer.GetMSTemplateByLabel(self.microserviceLabel)
				#if microservice == None:
					#self.running = False
					#break

				microservice = self.apiServer.GetMsByMsLabel(self.microserviceLabel)

				if microservice is not None:
					#eps = self.apiServer.GetEndPointsByLabel(self.deploymentLabel, ms)
					eps = self.apiServer.GetEndPoints()
					pods = []
					for pod in self.apiServer.GetPending():
							if pod.microserviceLabel == self.microserviceLabel:
								pods.append(pod)
					for ep in eps:
						if ep.microserviceLabel == self.microserviceLabel:
							pods.append(self.apiServer.GetPod(ep))
					availableCPUS = 0
					for pod in pods:
						availableCPUS+=pod.available_cpu
					if len(pods) == 0:
						averageUtil = 0
					else:
						averageUtil = (microservice.cpuCost*len(pods)-availableCPUS)/(microservice.cpuCost*len(pods))
					newReps = math.ceil(microservice.currentReplicas * averageUtil/self.setPoint)
					if newReps < self.minReps:
						microservice.expectedReplicas = self.minReps
					elif newReps > self.maxReps:
						microservice.expectedReplicas = self.maxReps
					else:
						microservice.expectedReplicas = newReps
					
			time.sleep(self.time)
		print("HPA Shutdown")
