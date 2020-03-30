import re
import requests
import os.path
import sys
import argparse
from bs4 import BeautifulSoup
from math import ceil

# colors
GREEN="\033[0;32m"
END_COLOR="\033[0m"

# constants
DEFAULT_NUM_DOWNLOADS = 20
DEFAULT_RESOLUTION = '3360x2100'
NUM_ITEMS_PER_PAGE = 10 # From website
DOMAIN = 'https://interfacelift.com'
FETCH_URL = DOMAIN + '/wallpaper/downloads/date/widescreen'

# Interfacelift helpers
def get_fetch_url(url, resolution, page_num):
    return FETCH_URL + '/{}/index{}.html'.format(resolution, page_num)

def get_num_pages(num_to_download):
    return int(ceil(num_to_download * 1.0 / NUM_ITEMS_PER_PAGE))

def get_colored(statement, color=GREEN):
  return '{color}{statement}{end_color}'.format(
    color=color,
    statement=statement,
    end_color=END_COLOR
  )

def download(url, filepath):
    with open(filepath, 'wb') as handle:
        res = requests.get(url, stream=True)
        for block in res.iter_content(1024):
            if not block:
                break
            handle.write(block)

def scrape_download_urls(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    containers = soup.find_all('div', id=re.compile('^download_'))
    return [c.find('a')['href'] for c in containers]

def main(num_to_download, save_dir, resolution, new_files_only):
    num_downloaded = 0
    print('***Downloading to directory {}'.format(get_colored(save_dir)))
    # Crawl through pages
    for page_num in range(1, get_num_pages(num_to_download) + 1):
        # Get content to parse
        url = get_fetch_url(FETCH_URL, resolution, page_num)
        for wp_url in scrape_download_urls(url):
            wp_filename = wp_url.split('/')[-1]
            # Check if wallpaper already exists
            wp_filepath = os.path.join(save_dir, wp_filename)
            if new_files_only and os.path.isfile(wp_filepath):
                print('{} exists, skipping...'.format(get_colored(wp_filepath)))
            else:
                # Downloaded enough
                if num_downloaded == num_to_download:
                    return
                # Otherwise download
                print('Downloading {}...'.format(get_colored(wp_filename)))
                download(DOMAIN + wp_url, wp_filepath)
                num_downloaded += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Downloads wallpapers from interfacelift.com')
    # Add args
    parser.add_argument('-a', '--amount', type=int, required=False, default=DEFAULT_NUM_DOWNLOADS,
        help='number of wallpapers to download (default {})'.format(DEFAULT_NUM_DOWNLOADS))
    parser.add_argument('-d', '--dir', type=str, required=True,
        help='directory to download wallpapers')
    parser.add_argument('-r', '--resolution', type=str, required=False, default=DEFAULT_RESOLUTION,
        help='wallpaper resolution (default {}), supported: 3440x1440, 2560x1080, 5120x2880, 4096x2160, 3840x2400, 3840x2160, 3360x2100, 3200x1800, 2880x1800, 2880x1620, 2560x1600, 2560x1440, 1920x1200, 1680x1050, 1600x900, 1440x900, 1280x800, 1600x2560, 1200x1920, 1080x1920'.format(DEFAULT_RESOLUTION))
    parser.add_argument('--newonly', action="store_true", required=False, default=False,
        help='only downloads new wallpapers not in directory')
    args = parser.parse_args()
    main(args.amount, args.dir, args.resolution, args.newonly)
