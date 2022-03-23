# import streamlit and other libraries
import streamlit as st
from requests_html import HTMLSession
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Book Scraper",
    page_icon="📚")

# give our application a title
st.title("Real-time web scraper with Python")


# add our web scraping code
session = HTMLSession()
main_url = "http://books.toscrape.com/"
main_page = session.get(main_url)

navlinks = "div.side_categories>ul.nav.nav-list>li>ul>li>a"
genres = [element.text for element in main_page.html.find(navlinks)]
list_urls = [
    f"{main_url}/{element.attrs['href']}" for element in main_page.html.find(navlinks)
]
genre_urls = dict(zip(genres, list_urls))


#@st.cache
def data_extract(genre):
    webpage = genre_urls.get(genre)
    webpage = session.get(webpage)
    
    number = st.slider("Number of books to show", 1, 11, 5)
    urls = [
        element.attrs["href"].strip("../")
        for element in webpage.html.find("div.image_container>a")
    ]
    urls = urls[:number]
    titles = [element.attrs["title"] for element in webpage.html.find("h3>a")]
    titles = titles[:number]
    imgs = [
        element.attrs["src"].strip("../")
        for element in webpage.html.find("div.image_container>a>img")
    ]
    imgs = ['https://books.toscrape.com/' + img for img in imgs]
    imgs = imgs[:number]

    ratings = [
        element.attrs["class"][-1] for element in webpage.html.find("p.star-rating")
    ]
    ratings = ratings[:number]

    prices = [element.text for element in webpage.html.find("p.price_color")]
    prices = prices[:number]

    availability = [element.text for element in webpage.html.find("p.instock")]
    availability = availability[:number]

    data = dict(
        Title=titles,
        URL=urls,
        SourceImage=imgs,
        Rating=ratings,
        Price=prices,
        Availability=availability,
    )
    # save to csv file 
    df = pd.DataFrame(data)
    file_name = f"{genre}_books.csv"
    return df, file_name


# add a sidebar to select genre
option = st.sidebar.selectbox("Genres", genres)

# show the dataframe with a big size window
df_books_scrape, file_name = data_extract(option)
st.dataframe(df_books_scrape)
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv_file = convert_df(df_books_scrape)

st.download_button(
    label="Download data as CSV",
    data=csv_file,
    file_name=file_name,
    mime='text/csv'
)
# convert ratings words to numeric ratings
def convert_rating(rating):
    if rating == "One":
        return 1
    elif rating == "Two":
        return 2
    elif rating == "Three":
        return 3
    elif rating == "Four":
        return 4
    elif rating == "Five":
        return 5
    else:
        return 0

#apply convert_rating to ratings column
df_books_scrape['Rating'] = df_books_scrape['Rating'].apply(convert_rating)
# order the dataframe by rating
df_books_scrape = df_books_scrape.sort_values(by='Rating', ascending=False)

def show_book_data(df):
    col1, col2, col3, col4 = st.columns((1, 1, 1, 2))
    imgs = df['SourceImage']
    titles = df['Title']
    prices = df['Price']
    ratings = df['Rating']
    for img, title, rating, price in zip(imgs, titles, ratings, prices):
        cols = st.columns(4)
        cols[0].image(img, width=100)
        cols[1].write(title)
        random_price = np.random.randint(-10, 10)
        cols[2].metric('Price', price, str(random_price) + '£')
        random_rating = np.random.randint(-4, 4)
        cols[3].metric("Rating", rating, str(random_rating) + '★')


st.subheader("Book Details Order by Rating")
show_book_data(df_books_scrape)
