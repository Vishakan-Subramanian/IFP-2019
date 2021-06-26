# IFP-2019
Content related to the Internally Funded Project - 2019 --- IoT Based Air Pollution Monitoring and Prediction

Done by: 

S K Srinithyee
N Venkataraman
S Vishakan


## Hosting with Heroku:
1. Create an account in Heroku.
2. Download Git client & Heroku CLI tool.
3. Clone this repository.
4. Run this command: `heroku create --buildpack https://github.com/virtualstaticvoid/heroku-buildpack-r.git` to create the buildpack.
5. Run this command: `git push heroku master` to push the buildpack and deploy it on Heroku.
6. If build/push fails, change the stack to Heroku-16/Heroku-18 using the command `heroku stack: set heroku-18` and retry.
7. Open the link obtained in the terminal after the deployment is done to view the website.

### Currently hosted in ShinyApps.io

