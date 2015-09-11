# importing functionality
import os
import sys

# import libs
from App.FrameworkScan.WordPressScan.WordPressScan import WordPressScan

# ini variables
pathApp = os.getcwd().replace('\\', '/')
pathFramework = pathApp + '/Workspace'

# init classes
fwScan = WordPressScan(pathFramework)

scanResults = fwScan.repo()

print(scanResults)
