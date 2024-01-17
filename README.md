In this project we are trying to identify whether there is any correlation between number of museum visitors and population of cities where those museums are located. For this purpose we created a dataset based on top visited museums from Wikipedia https://en.wikipedia.org/wiki/List_of_most-visited_museums and population data from https://simplemaps.com/data/world-cities. Data about population density is taken from Google/Wikipedia.


Docker image available on Dockerhub: 

        - docker pull mlmaster/top_museums_corr:<version>

To view the analysis in jupyter notebook in container: 

	- docker run -p 5000:8888 mlmaster/top_museums_corr (replace host port 5000 if needed)

	- in the browser open one of the URLs from docker startup logs (starts with  "http://127.0.0.1:8888/" and includes access token, make sure to update the port to match the one 
 	  specified in previous step eg 5000)

	- run the notebook eg http://127.0.0.1:5000/lab/tree/top_museums/notebooks/top_museums.ipynb
 