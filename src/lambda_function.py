from scraper import RealEstateScraper
from parameters import pararius_dict
import time
from selenium.webdriver.common.keys import Keys


def lambda_run(docker_run=True):
    scraper = RealEstateScraper(pararius_dict(), docker_run)

    results = scraper.read_base_page()
    scraper.close()
    print(results)

    return results


def lambda_handler(*args, **kwargs):
    lambda_run()


if __name__ == "__main__":
    lambda_run(docker_run=False)