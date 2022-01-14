import pickle
import data_cleaner


def pararius_dict():
    pararius = {
        'self': 'Pararius',
        'base_page': 'https://www.pararius.nl/koopwoningen/amsterdam',
        'page_base_url': 'https://www.pararius.nl/koopwoningen/amsterdam/page-',
        'max_page_find': ['a', 'class', 'pagination__link', data_cleaner.returns_int_only],
        'index_page_blocks': ['li', 'class', 'search-list__item search-list__item--listing'],
        'index_page_attributes':
            [['title', 'a', 'class', 'listing-search-item__link listing-search-item__link--title', False],
             ['link', 'a', 'class', 'listing-search-item__link listing-search-item__link--title', True],
             ['price_raw', 'div', 'class', 'listing-search-item__price', False]],

        'listings_page_attributes':
            [['address', 'h1', 'class', 'listing-detail-summary__title', False],
             ['postcode', 'div', 'class', 'listing-detail-summary__location', False],
             ['available_from', 'dd', 'class',
              'listing-features__description listing-features__description--offered_since', False],
             ['price_page', 'dd', 'class',
              'listing-features__description listing-features__description--for_sale_price',
              False],
             ['square_meters', 'dd', 'class',
              'listing-features__description listing-features__description--surface_area', False],
             ['volume', 'dd', 'class', 'listing-features__description listing-features__description--volume', False],
             ['type_building', 'dd', 'class',
              'listing-features__description listing-features__description--dwelling_type', False],
             ['building_status', 'dd', 'class',
              'listing-features__description listing-features__description--construction_type', False],
             ['build_date', 'dd', 'class',
              'listing-features__description listing-features__description--construction_period', False],
             ['total_rooms', 'dd', 'class',
              'listing-features__description listing-features__description--number_of_rooms', False],
             ['bedrooms', 'dd', 'class',
              'listing-features__description listing-features__description--number_of_bedrooms', False],
             ['bathrooms', 'dd', 'class',
              'listing-features__description listing-features__description--number_of_bathrooms', False],
             ['balcony', 'dd', 'class', 'listing-features__description listing-features__description--balcony',
              False],
             ['garden', 'dd', 'class', 'listing-features__description listing-features__description--garden',
              False],
             ['shed', 'dd', 'class', 'listing-features__description listing-features__description--storage',
              False]]
    }
    return pararius