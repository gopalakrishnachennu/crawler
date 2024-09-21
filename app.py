
import streamlit as st
from scraper import scrape_google_maps
from business import BusinessList

def main():
    st.title("Google Maps Scraper")

    # User inputs
    search_query = st.text_input("Enter Search Term")
    radius = st.number_input("Radius (in miles)", min_value=1, max_value=100, value=10)
    total_results = st.number_input("Number of Results", min_value=1, max_value=100, value=10)

    if st.button("Scrape Google Maps"):
        # Include radius in the search query
        full_search_query = f"{search_query} within {radius} miles"
        business_list = scrape_google_maps(full_search_query, total_results)
        
        # Display the data in a table
        df = business_list.dataframe()
        st.dataframe(df)
        
        # Button to download data as CSV
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'{search_query}_google_maps_data.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
