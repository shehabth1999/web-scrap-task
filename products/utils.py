from bs4 import BeautifulSoup
import requests, re

def get_default_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track Request Header
        "Cache-Control": "no-cache",
    }

class ProductScraping:
    def __init__(self, product_link, soup = None, headers = None):
        self.product_link = product_link
        self.soup = soup
        self.headers = headers
        
        # main data and error result
        self.data = {}
        self.errors = {}

    def get_soup(self):
        """
        Retrieve BeautifulSoup object from Amazon product page
        """
        # need to cache requests here for performance 100 seconds
        try:
            if self.headers is None:
                self.headers = get_default_headers()
            response = requests.get(self.product_link, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except Exception as e:
            self.errors['get_soup'] = str(e)
            return None
        
    def is_work(self):
        """
        Check if the get_soup method works properly and No errors occurred
        """
        if not self.soup:
            self.soup = self.get_soup()
        if not self.soup:
            return False
        self.extract_data()
        return len(self.errors) == 0

    def get_title(self):
        """
        Retrieve product title from BeautifulSoup object
        """
        try:
            title = self.soup.select_one('#productTitle').text.strip() 
            if title:
                self.data['title'] = title
                return title
            else:
                self.errors['get_title'] = 'No title found'
        except Exception as e:
            self.errors['get_title'] = str(e)
            return None

    def get_rating(self):
        """
        Retrieve product rating from BeautifulSoup object
        """
        try:
            rating = self.soup.select_one('#acrPopover').attrs.get('title').replace(' out of 5 stars', '')
            if rating:
                self.data['rating'] = rating
                return rating
            else:
                self.errors['get_rating'] = 'No rating found' 
        except Exception as e:
            self.errors['get_rating'] = str(e)
            return None

    def get_image(self):
        """
        Retrieve product image URL from BeautifulSoup object
        """
        try:
            image = self.soup.select_one('#landingImage').attrs.get('src') 
            if image:
                self.data['image'] = image
                return image
            else:
                self.errors['get_image'] = 'No image found'
        except Exception as e:
            self.errors['get_image'] = str(e)
            return None

    def get_price(self):
        """
        Retrieve product price from BeautifulSoup object
        """
        try:
            whole_element = self.soup.select_one('.a-price-whole')
            fraction_element = self.soup.select_one('.a-price-fraction')
            symbol_element = self.soup.select_one('.a-price-symbol')
            if whole_element and fraction_element and symbol_element:
                price = f"{symbol_element.text.strip()}{whole_element.text.strip()}{fraction_element.text.strip()}"
                price_float_str = '{:.2f}'.format(float(re.findall(r'\d+\.\d+', price)[0]))
                self.data['price'] = price_float_str
                return price
        except Exception as e:
            self.errors['get_price'] = str(e)

    def get_details(self):
        """
        Retrieve product details from BeautifulSoup object
        """
        try:
            description_scope = self.soup.select_one('#productFactsDesktopExpander')
            details_elements = description_scope.select('.product-facts-detail')
            details =  [element.text.strip() for element in details_elements]
            self.data['details'] = details
            return details
        except Exception as e:
            self.errors['get_details'] = str(e)
            return None

    def get_description(self):
        """
        Retrieve product description from BeautifulSoup object
        """
        try:
            description_scope = self.soup.select_one('#productFactsDesktopExpander')
            description_elements = description_scope.select('ul li span')
            description = [element.text.strip() for element in description_elements]
            self.data['description'] = description
            return description
        except Exception as e:
            self.errors['get_description'] = str(e)
            return None

    def extract_data(self):
        """
        Retrieve data from Amazon product page
        """
        try:
            self.get_title()
            self.get_rating()
            self.get_price()
            self.get_image()
            self.get_details()
            self.get_description()
        except Exception as e:
            self.errors['extract_data'] = str(e)

    def scraping_errors(self):
        return self.errors
    
    def scraping_result(self):
        return self.data