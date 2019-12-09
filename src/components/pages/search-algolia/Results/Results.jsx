import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import React from 'react'

import { formatRecommendationDates } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import Icon from '../../../layout/Icon/Icon'

const Results = ({searchResults, userLatitude, userLongitude}) => (
  <div className="search-results">
    {searchResults.map(searchResult => (
      <Link
        key={searchResult.objectID}
        to={`/recherche-algolia/details/${searchResult.offer.id}/vide`}
      >
        <div className="search-result">
          <img
            alt=""
            className="image-search-result"
            src={searchResult.offer.thumbUrl}
          />
          <div className="details-search-result">
            <h2 className="details-search-result-title">
              {searchResult.offer.name}
            </h2>
            <p className="details-search-result-type">
              {searchResult.offer.label}
            </p>
            <p className="details-search-result-date">
              {formatRecommendationDates(
                searchResult.offer.departementCode,
                searchResult.offer.dateRange
              )}
            </p>
            <p className="details-search-result-distance">
              {getHumanizeRelativeDistance(
                userLatitude,
                userLongitude,
                searchResult._geoloc.lat,
                searchResult._geoloc.lng
              )}
            </p>
          </div>
          <div className="arrow-search-result">
            <Icon
              className="teaser-arrow-img"
              svg="ico-next-S"
            />
          </div>
        </div>
      </Link>
    ))}
  </div>
)

Results.defaultProps = {
  searchResults: [],
  userLatitude: null,
  userLongitude: null,
}

Results.propTypes = {
  searchResults: PropTypes.arrayOf(PropTypes.shape({
    offer: PropTypes.shape({
      dateRange: PropTypes.arrayOf([]),
      departementCode: PropTypes.number,
      name: PropTypes.string,
      thumbUrl: PropTypes.string,
      type: PropTypes.string,
    }),
    _geoloc: PropTypes.shape({
      lat: PropTypes.number,
      long: PropTypes.number,
    }),
    objectID: PropTypes.string,
  })),
  userLatitude: PropTypes.number,
  userLongitude: PropTypes.number,
}

export default Results
