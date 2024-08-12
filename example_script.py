import chromedriver_autoinstaller

from src.GoogleTrendsScraper import GoogleTrendsScraper

chromedriver_autoinstaller.install()

gts = GoogleTrendsScraper(sleep=2, headless=True)
data = gts.get_trends("fight the flu", '2020-01-01', '2024-01-01', 'US', time_scale="weekly")

del gts

print(data)



