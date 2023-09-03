# The python libraries which works with this code
import time
from playwright.async_api import async_playwright
import asyncio
import csv  # used for making csv files
import lxml # used for parsing html
import requests # Used for making requests to the website
from bs4 import BeautifulSoup # Beautifulsoup is used for extracting information in the html

# The main function which has all the running code
async def main():
    # These are the headers which are sent along with a request to the webpage
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.56 Safari/537.36",
        "Referer": "https://www.example.com",
        "Accept-Language": "en-US,en;q=0.9"
    }
    url = "https://www.blockdata.tech/markets/use-cases" # This is the url which contains all the use cases links

    response = requests.get(url, headers=headers)   # The response which is made by making a request to the blockdata sote

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, "lxml")

    # Find the containers that hold the provider information
    a_tags = soup.find_all('a')

    # Getting the href in the a tags
    links = [a["href"] for a in a_tags]

    # Filtering the links and getting the links which starts with the 'use-cases' string
    filtered_links = [link for link in links if link.startswith("use-cases")]

    base_url = 'https://www.blockdata.tech/markets/' # The base url which has all the links with the use cases
    use_cases_url_list = [] #List which will hold the href links i get from the base url

    # This loop iterates and concatenates the use cases with the base url - appending the full/complete url into the use_cases_url_list
    for use_case in filtered_links:
        url = base_url + use_case
        use_cases_url_list.append(url)
    
    profiles_list = []  # This list will hold all the profiles on the use cases web pages
    # This loop iterates through the url of the use cases and make requests to the current index, scraps the profile links and appends them -
    # to the 'profiles_list' list
    for use_case_url in use_cases_url_list:
        response = requests.get(use_case_url, headers=headers)  
        soup = BeautifulSoup(response.content, "lxml")
        prettified_html = soup.prettify()
        link_tags = soup.find_all("a", class_="MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButtonBase-root index-button css-sgl86c")
        links = [a["href"] for a in link_tags]
        for link in links:
            if link not in profiles_list:
                profiles_list.append(link)

    # This loop below will iterate through each profile in the profiles_list and appends it to the base_url to make a valid url of a profile
    base_url = "https://www.blockdata.tech"
    full_profile_url_list = []
    for profile in profiles_list:
        full_url = base_url + profile
        full_profile_url_list.append(full_url)
    
    # print(full_profile_url_list)
    # test_profiles_list_urls = [ 'https://www.blockdata.tech/profiles/liink-pre-interbank-information-network-by-jpmorgan'] # just a list i used for testing

    # A csv writer, which will write the output to three csv files.
    with open('Blockdata-Partners-Customers.csv', 'w', newline='') as partnerscsvfile, \
         open('Blockdata-Products.csv', 'w', newline='') as productscsvwriter, \
         open('Blockdata-News.csv', 'w', newline='') as newscsvwriter:

        # writing to each respective csv file below
        partners_csv_writers = csv.writer(partnerscsvfile)
        partners_csv_writers.writerow(["Profile Url","Company Name", "List of Partners"])

        products_csv_writers = csv.writer(productscsvwriter)
        products_csv_writers.writerow(["Profile Url", "Company Name", "List of Products"])

        news_csv_writers = csv.writer(newscsvwriter)
        news_csv_writers.writerow(["Profile Url", "Company Name", "List of News"])

        # The loop below will iterate through each profile url to scrap data
        for url in full_profile_url_list:
            # This block below will scrap the - Customers/Partners section
            name_of_vendor = url.split('/')[-1].capitalize()    #This is the name of the vendor which is being scrapped
            # Making an async call using playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=False) # Initiating a browser and launching it in headless mode

                page = await browser.new_page()
                await page.goto(url)
                await page.wait_for_timeout(3000)

                # Find the desired partner element using the 'Customers / Partners' string found in that section
                all_divs = await page.query_selector_all('.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh')
                partners_matching_div_found = [p for p in all_divs if 'Customers / Partners' in await p.text_content()]
                    
                # code for clicking all the buttons on the partners section if its found
                # if the required div element is found, then code below will execute
                partners_list = []
                if partners_matching_div_found:
                    partners = [p for p in await page.query_selector_all(
                                    '.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh') if
                                            'Customers / Partners' in await p.text_content()][0] # The partners div is found at the element 0 as it is the filtered result
                    
                    # While the div element contains the show more button it will loop until its no longer found / until has_more = False
                    has_more = True
                    while has_more:   
                        # Look for the 'Show more' button
                        show_more_btn = [p for p in await partners.query_selector_all(
                            '.MuiButton-root.MuiButton-text.MuiButton-textPrimary.MuiButton-sizeSmall.MuiButton-textSizeSmall.MuiButtonBase-root.css-x16yd0') if
                                    'Show more' in await p.text_content()] # Selecting the 'Show more' button on the page

                        # If 'Show more' button is found, click it
                        if len(show_more_btn) > 0:
                            print("Found show more button...")
                            await show_more_btn[0].scroll_into_view_if_needed()
                            await show_more_btn[0].click()
                            time.sleep(3)
                        else:
                            has_more = False
                            
                        # Check for the modal if its open, close btn should be clicked
                        modal_btn = await page.query_selector('.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-colorPrimary.MuiIconButton-sizeLarge.css-yqgmlj')
                        if modal_btn:
                            await modal_btn.click()    

                    partners_html = await partners.inner_html() # Getting the partners html
                    soup = BeautifulSoup(partners_html, 'lxml') # Using beautiful soup to parse the html

                    # Selecting all the sub - divs in the partnership div element
                    all_partnership_divs = soup.find_all('div', class_="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation1 MuiCard-root eoebmzv1 css-1uxl6eo")
                    
                    # Object which will store the partners info
                    partners_object = {}
                    if all_partnership_divs:
                        # Looping through the div elements to select the information nested inside their elements
                        for partnership in all_partnership_divs:  
                            date = partnership.find('div', class_="MuiTypography-root MuiTypography-caption MuiTypography-alignCenter css-1e0ac1u")
                            # Getting the text content in the html
                            if date:
                                date = date.get_text()

                            # Finding the p tag element with that specific class_
                            partnership_name = partnership.find('p', class_="MuiTypography-root MuiTypography-body1 MuiTypography-alignCenter MuiTypography-gutterBottom css-ed9ivh")

                            if partnership_name:
                                partnership_name = partnership_name.get_text()   # Getting the text content in the html
                            
                            profile_link_div = partnership.find('div', class_="MuiCardActions-root css-jo6j44")

                            if profile_link_div:
                                profile_link = profile_link_div.find('a')
                                profile_link = profile_link["href"]
                                
                            partners_object = {
                                    "Date" : date,
                                    "Partnership Name" : partnership_name,
                                    "Profile Link" : profile_link
                                }

                            partners_list.append(partners_object)
                else:
                    partners_list = 'N/A'   # If the partners div is not found then set the list to N/A

                # name_of_vendor = url.split('/')[-1].capitalize()
                
                data = [url,name_of_vendor, partners_list]  # The data which is obtained from scrapping the web page
                partners_csv_writers.writerow(data) # Writing the list to a csv row
                await browser.close()   # Close the browser
            
            # # Started here for - Products
            async with async_playwright() as pw:
                browser = await pw.chromium.launch( headless=False )

                page = await browser.new_page()
                await page.goto(url)
                await page.wait_for_timeout(3000)

                # Find the desired partner element
                all_divs = await page.query_selector_all('.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh')
                products_matching_div_found = [p for p in all_divs if 'Products' in await p.text_content()]

                products_list = []
                if products_matching_div_found:
                    products = [p for p in await page.query_selector_all(
                                    '.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh') if
                                            'Products' in await p.text_content()][0]
                    
                    has_more = True
                    while has_more:
                            
                        # Look for the 'Show more' button
                        show_more_btn = [p for p in await products.query_selector_all(
                            '.MuiButton-root.MuiButton-text.MuiButton-textPrimary.MuiButton-sizeSmall.MuiButton-textSizeSmall.MuiButtonBase-root.css-x16yd0') if
                                    'Show more' in await p.text_content()]

                        # If 'Show more' button is found, click it
                        if len(show_more_btn) > 0:
                            print("Found show more button...")
                            await show_more_btn[0].scroll_into_view_if_needed()
                            await show_more_btn[0].click()
                            time.sleep(3)
                        else:
                            has_more = False
                            
                        # Check for the modal if its open, close btn should be clicked
                        modal_btn = await page.query_selector('.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-colorPrimary.MuiIconButton-sizeLarge.css-yqgmlj')
                        if modal_btn:
                            await modal_btn.click() 
                    
                    products_html = await products.inner_html()
                    soup = BeautifulSoup(products_html, 'lxml')
                    # Will continue from here with using bs4

                    all_products_divs = soup.find_all('div', class_="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation1 MuiCard-root e169x05j0 css-s6xax9")

                    product_object = {}
                    if all_products_divs:
                        for product in all_products_divs:
                            #1 - get the status
                            status = product.find('div', class_="MuiTypography-root MuiTypography-caption MuiTypography-gutterBottom index-status index-statusGreen css-1upipcb")
                            if status:
                                status = status.get_text()

                            #2 - product name
                            product_name = product.find('p', class_="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom index-name css-10xgjol")

                            if product_name:
                                product_name = product_name.get_text()
                            
                            #3 - Get the product profile link
                            product_profile_link_div = product.find('div', class_="MuiCardActions-root css-jo6j44")

                            if product_profile_link_div:
                                product_profile_link = product_profile_link_div.find('a')

                                if product_profile_link:
                                    product_profile_link = product_profile_link["href"]
                            
                            product_object = {
                                "Product Name":product_name,
                                "Status" : status,
                                "Profile Link" : product_profile_link
                            }
                            products_list.append(product_object)
                else:
                    products_list = 'N/A'

                data = [url,name_of_vendor, products_list]
                products_csv_writers.writerow(data)
                await browser.close()

            # Started here for - News
            async with async_playwright() as pw:
                browser = await pw.chromium.launch( headless=True )

                page = await browser.new_page()
                await page.goto(url)
                await page.wait_for_timeout(3000)

                # Find the desired news element
                all_divs = await page.query_selector_all('.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh')
                news_matching_div_found = [p for p in all_divs if 'News' in await p.text_content()]
                
                news_list = []
                if news_matching_div_found:
                    news = [p for p in await page.query_selector_all(
                                    '.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-7fmivh') if
                                            'News' in await p.text_content()][0]
                    
                    has_more = True
                    while has_more:   
                        # Look for the 'Show more' button
                        show_more_btn = [p for p in await news.query_selector_all(
                            '.MuiButton-root.MuiButton-text.MuiButton-textPrimary.MuiButton-sizeSmall.MuiButton-textSizeSmall.MuiButtonBase-root.css-x16yd0') if
                                    'Show more' in await p.text_content()]

                        # If 'Show more' button is found, click it
                        if len(show_more_btn) > 0:
                            print("Found show more button...")
                            await show_more_btn[0].scroll_into_view_if_needed()
                            await show_more_btn[0].click()
                            time.sleep(3)
                        else:
                            has_more = False
                            
                        # Check for the modal if its open, close btn should be clicked
                        modal_btn = await page.query_selector('.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-colorPrimary.MuiIconButton-sizeLarge.css-yqgmlj')
                        if modal_btn:
                            await modal_btn.click() 
                    
                    news_html = await news.inner_html()
                    
                    soup = BeautifulSoup(news_html, 'lxml')
                    #Will continue from here with using bs4
                    all_news_divs = soup.find_all('div', class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 css-15j76c0")
                    if all_news_divs:
                        for news_div in all_news_divs:
                            sub_div = news_div.find('div', class_="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation1 e1jrtzgh5 css-1xz7kw3")

                            #1 - The link to news article
                            if sub_div:
                                link_to_news_article = sub_div.find('a', class_="css-1tnz5rr e1jrtzgh4")
                                if link_to_news_article:
                                    link_to_news_article = link_to_news_article["href"]
                            
                            #2 - Going for the title

                            if sub_div:
                                sub_sub_div = sub_div.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2 css-isbt42")

                                if sub_sub_div:
                                    sub_sib_sub_div  = sub_sub_div.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-spacing-xs-2 MuiGrid-direction-xs-column MuiGrid-grid-xs-true css-1mf8c4o")

                                    if sub_sib_sub_div:
                                        title = sub_sib_sub_div.find("div", class_="MuiTypography-root MuiTypography-body3 MuiTypography-gutterBottom e1jrtzgh1 css-1nzn14v")

                                        short_news = sub_sib_sub_div.find("div", class_="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom css-12a9729")

                                        title = title.get_text()
                                        short_news = short_news.get_text()

                                        div_with_info = sub_sib_sub_div.find("div", class_="MuiGrid-root MuiGrid-item css-1wxaqej")

                                        if div_with_info:
                                            div_with_info = div_with_info.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2 css-yvl9ay")

                                            if div_with_info:
                                                parent = div_with_info.find("div", class_="MuiGrid-root MuiGrid-item css-1wxaqej")

                                                if parent:
                                                    time_posted = parent.find("p", class_="MuiTypography-root MuiTypography-body1 css-yt6mq")
                                                    time_posted = time_posted.get_text()
                                                
                                                if parent:
                                                    news_category_div = parent.find("div", class_="MuiChip-root MuiChip-filled MuiChip-sizeSmall MuiChip-colorSecondary MuiChip-filledSecondary e1jrtzgh0 css-775b0")
                                                    
                                                    if news_category_div:
                                                        news_category = news_category_div.find("span", class_="MuiChip-label MuiChip-labelSmall css-tavflp")
                                                        news_category = news_category.get_text()
                            
                            #Now creating the news object
                            news_object = {
                                "Link To News Article" : link_to_news_article,
                                "Title" : title,
                                "Short News" : short_news,
                                "Time Posted" : time_posted,
                                "News Category" : news_category
                            }
                            news_list.append(news_object)
                else:
                    news_list = 'N/A'

                data = [url,name_of_vendor, news_list]
                news_csv_writers.writerow(data)
                await browser.close()        
          
        #Every code under this is out of the loop
        print("Done")


if __name__ == '__main__':
    asyncio.run(main())

