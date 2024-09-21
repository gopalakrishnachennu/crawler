from playwright.sync_api import sync_playwright
from business import Business, BusinessList
import streamlit as st
from utils import extract_coordinates_from_url

def scrape_google_maps(search_for, total):
    """Scrapes Google Maps for the specified search term."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Open Google Maps
        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)

        # Perform the search
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(3000)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        # Scroll and load listings
        listings = []
        previously_counted = 0
        retry_count = 0
        
        while retry_count < 3:  # Retry up to 3 times if needed
            try:
                # Hover over elements to load them
                page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                current_count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                
                if current_count >= total:
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    break
                elif current_count == previously_counted:
                    # If no new elements were loaded, break
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                    break
                else:
                    previously_counted = current_count
            except Exception as e:
                retry_count += 1
                st.warning(f"Retrying due to error: {e}")
                page.reload()
                page.wait_for_timeout(5000)

        business_list = BusinessList()

        # Scraping
        for listing in listings:
            try:
                listing.click()
                page.wait_for_timeout(5000)

                name_attibute = 'aria-label'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                business = Business()

                # Check if the attribute is not None
                name_value = listing.get_attribute(name_attibute)
                if name_value:
                    business.name = name_value

                if page.locator(address_xpath).count() > 0:
                    business.address = page.locator(address_xpath).all()[0].inner_text()
                if page.locator(website_xpath).count() > 0:
                    business.website = page.locator(website_xpath).all()[0].inner_text()
                if page.locator(phone_number_xpath).count() > 0:
                    business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                if page.locator(review_count_xpath).count() > 0:
                    business.reviews_count = int(
                        page.locator(review_count_xpath).inner_text()
                        .split()[0]
                        .replace(',', '')
                        .strip()
                    )
                if page.locator(reviews_average_xpath).count() > 0:
                    reviews_average_value = page.locator(reviews_average_xpath).get_attribute(name_attibute)
                    if reviews_average_value:
                        business.reviews_average = float(
                            reviews_average_value.split()[0].replace(',', '.').strip()
                        )
                
                # Extract coordinates safely
                business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                business_list.business_list.append(business)
            except Exception as e:
                st.error(f'Error occurred while scraping a listing: {e}')

                
        browser.close()
        return business_list
