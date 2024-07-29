import chromedriver_autoinstaller

from src.GoogleTrendsScraper import GoogleTrendsScraper

chromedriver_autoinstaller.install()

gts = GoogleTrendsScraper(sleep=2, headless=True)
data = gts.get_trends(["water", "snake"], '2018-01-01', '2019-02-01', 'US', time_scale="monthly")

del gts

print(data)



