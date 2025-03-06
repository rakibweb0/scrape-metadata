import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from slugify import slugify

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

# Function to get metadata
def get_meta_data(url):
    try:
        html = fetch_page_source(url)
        if not html:
            return {"URL": url, "Title": "Error", "Description": "Error", "OG Image": "Error", "Slug": "Error"}
        
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title Found"
        description = soup.find("meta", attrs={"name": "description"})
        og_image = soup.find("meta", property="og:image")
        description = description["content"].strip() if description else "No Description Found"
        og_image = og_image["content"].strip() if og_image else "No OG Image Found"

        slug = slugify(title)

        return {
            "URL": url,
            "Title": title,
            "Description": description,
            "OG Image": og_image,
            "Slug": slug
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return {"URL": url, "Title": "Error", "Description": str(e), "OG Image": "Error", "Slug": "Error"}

# Streamlit UI to upload text file with URLs
st.title("Website Meta Data Extractor")

# File uploader
uploaded_file = st.file_uploader("Choose a text file with URLs like: https://www.example.com", type="txt")

if uploaded_file is not None:
    # Read the uploaded file and extract URLs
    urls = uploaded_file.getvalue().decode("utf-8").splitlines()

    # Button to trigger data scraping
    if st.button("Get Meta Data"):
        # Process all the URLs
        data = [get_meta_data(url) for url in urls]

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Display the DataFrame
        st.write(df)

        # Save the data to a CSV file
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name="meta_data.csv",
            mime="text/csv"
        )
    else:
        st.write("Click the button to get the meta data.")

else:
    st.write("Upload a text file to get started.")