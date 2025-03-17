import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from slugify import slugify
from urllib.parse import urljoin
import json

# Function to fetch page content
def fetch_page_source(url, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.Timeout:
        print(f"Request Timeout: {url} took longer than {timeout} seconds to respond.")
        return None
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to get favicon
def fetch_favicon(soup, base_url):
    rels = ["icon", "shortcut icon", "apple-touch-icon"]
    for rel in rels:
        tag = soup.find("link", rel=rel)
        if tag and tag.get("href"):
            return urljoin(base_url, tag["href"])
    return "No Favicon Found"

# Function to get metadata
def get_meta_data(url):
    try:
        html = fetch_page_source(url)
        if not html:
            return {
                "name": "Error",
                "slug": "Error",
                "shortDescription": "Error",
                "description": "Error",
                "toolUrl": url,
                "ogImage": "Error",
                "favicon": "Error",
                "priceModel": "free",
                "status": "inactive",
                "integration": [],
                "tags": [],
                "categoryIds": [],
                "userInfo": {
                    "name": "raqibnur",
                    "email": "raqibnur24@gmail.com"
                }
            }
        
        soup = BeautifulSoup(html, "html.parser")
        #get title
        name = soup.title.string.strip() if soup.title else "No Title Found"
        
        # get description
        description_tag = soup.find("meta", attrs={"name": "description"})
        shortDescription = description_tag["content"].strip() if description_tag else "No Description Found"
        
        # get og image
        og_image_tag = soup.find("meta", property="og:image")
        og_image = og_image_tag["content"].strip() if og_image_tag else "No OG Image Found"
        
        # get favicon
        favicon = fetch_favicon(soup, url)
        
        # convert title to slug
        slug = slugify(name)

        return {
            "name": name,
            "slug": slug,
            "shortDescription": shortDescription,
            "description": "",
            "toolUrl": url,
            "ogImage": og_image,
            "favicon": favicon,
            "priceModel": "free",
            "status": "active",
            "integration": [],
            "tags": [],
            "categoryIds": [],
            "userInfo": {
                "name": "raqibnur",
                "email": "raqibnur24@gmail.com"
            },
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return {
            "name": "Error",
            "slug": "Error",
            "shortDescription": str(e),
            "description": "Error",
            "toolUrl": url,
            "ogImage": "Error",
            "favicon": "Error",
            "priceModel": "free",
            "status": "inactive",
            "integration": [],
            "tags": [],
            "categoryIds": [],
            "userInfo": {
                "name": "raqibnur",
                "email": "raqibnur24@gmail.com"
            }
        }

# Streamlit UI to upload text file with URLs
st.title("Website Meta Data Extractor")

# File uploader
uploaded_file = st.file_uploader("Upload a text file with URLs (one per line)", type="txt")
if uploaded_file is not None:
    urls = uploaded_file.getvalue().decode("utf-8").splitlines()

    if st.button("Get Meta Data"):
        data = [get_meta_data(url) for url in urls]

        st.json(data)  # Display raw JSON in Streamlit

        # Save as JSON
        json_data = json.dumps(data, indent=2)

        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="meta_data.json",
            mime="application/json"
        )
    else:
        st.write("Click the button to fetch metadata.")
else:
    st.write("Please upload a .txt file to begin.")