# -- Abstract

# This serves as a documentation to the code which scraps the blockdata website. 
# The code begins with scrapping all the uses cases on the blockdata webpage. 
# It then goes to scrapping and storing all the profiles in the uses cases. 
# A single profile may appear twice, it might be found in two different use cases but this code 
# addresses that situation so that it is only scrapped once to avoid data redundancy and also to reduce the running 
# time of the web scrapper i.e., improve the efficiency of the code. After scrapping all the profiles, it then iterates 
# through the profiles and scrap the information for that profile. Each profile has seven sections so the first 
# script is responsible for scrapping the non-dynamic sections / sections which do not make use of show more buttons 
# which renders more information on the page after being clicked by the user and the second script scraps the more 
# complicated sections on the profile page which make use of show more buttons.

# The data scrapped in this code are stored as a single values, lists, dictionaries or a list containing dictionaries

# The code first scraps the href to the use cases on this web page - https://www.blockdata.tech/markets/use-cases
# The code then goes to scrap the profile pages links. For example for scrapping the access-control-system use-case -
# -it uses this url -> https://www.blockdata.tech/markets/use-cases/access-control-system 
# the last part 'access-control-system' changes depending on the use-case being scrapped

# The code then scraps at most 7 sections on the profile page, a profile might have less than 7 sections so it just stores 'N/A'
# for that particular section. For example it locates and 
# scraps a typical profile url like this -> https://www.blockdata.tech/profiles/sweatcoin

#For missing values the code just stores the string 'N/A'