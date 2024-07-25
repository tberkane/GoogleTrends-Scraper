import chromedriver_autoinstaller

from src.GoogleTrendsScraper import GoogleTrendsScraper

chromedriver_autoinstaller.install()

gts = GoogleTrendsScraper(sleep=2, headless=True)
data = gts.get_trends('flu', '2018-01-01', '2019-03-31', 'US')
del gts

print(data)

data.plot()


