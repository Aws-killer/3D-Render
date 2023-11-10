import asyncio
from playwright.async_api import async_playwright

async def extract_bootstrap_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to the Pixabay Sound Effects page
        await page.goto('https://pixabay.com/sound-effects/search/door%20creaking/')

        # Wait for the content to load (you can adjust the timeout as needed)
        # await page.wait_for_selector('.js-media-list-wrapper')
        # await page.wait_for_selector('.js-media-item')

        # Get the content of the 5th script tag
        # script_content = await page.evaluate('''() => {
        #     const scripty=document.querySelectorAll('script')[0];
        #     return scripty.content
        # }''')
        # print(script_content)
        # await page.evaluate(f'''{script_content}(''')
       
        page_content = await page.content()
        # Print the content of the 5th script tag
        # print(page_content)

        # Close the browser
        await browser.close()

# Run the extraction function
if __name__ == '__main__':
    asyncio.run(extract_bootstrap_data())
