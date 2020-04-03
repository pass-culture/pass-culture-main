import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { formatSearchResultDate } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import { formatResultPrice } from '../../../../utils/price'
import { DEFAULT_THUMB_URL } from '../../../../utils/thumb'

const Result = ({ result, geolocation, search }) => {
  const { _geoloc = {}, objectID, offer } = result
  const {
    dates,
    departementCode,
    id: offerId,
    isDuo,
    label,
    name,
    priceMin,
    priceMax,
    thumbUrl,
  } = offer
  const { latitude: userLatitude, longitude: userLongitude } = geolocation
  const { lat: venueLatitude, lng: venueLongitude } = _geoloc
  const thumbSrc = thumbUrl !== null ? thumbUrl : DEFAULT_THUMB_URL
  const formattedDate = formatSearchResultDate(departementCode, dates)
  const formattedPrice = formatResultPrice(priceMin, priceMax, isDuo)
  const canDisplayPrice = (priceMin && priceMax) || priceMin === 0
  const humanizedDistance = getHumanizeRelativeDistance(
    userLatitude,
    userLongitude,
    venueLatitude,
    venueLongitude
  )

  return (
    <Link
      key={objectID}
      to={`/recherche-offres/resultats/details/${offerId}${search}`}
    >
      <div className="result-wrapper">
        <img
          alt=""
          className="result-image"
          src={thumbSrc}
        />
        <div className="result-container">
          <div className="result-header">
            <h1 className="result-title">
              {name}
            </h1>
            {geolocation && humanizedDistance && (
              <span
                className="result-distance"
                data-test="result-distance-test"
              >
                {humanizedDistance}
              </span>
            )}
          </div>
          <p className="result-type">
            {label}
          </p>
          {formattedDate && (
            <p
              className="result-date"
              data-test="result-date-test"
            >
              {formattedDate}
            </p>
          )}
          {canDisplayPrice && (
            <p className="result-price">
              {formattedPrice}
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}

Result.defaultProps = {
  geolocation: {},
  result: {},
  search: '',
}

Result.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  result: PropTypes.shape({
    _geoloc: PropTypes.shape({
      lat: PropTypes.number,
      lng: PropTypes.number,
    }),
    offer: PropTypes.shape({
      dates: PropTypes.arrayOf(PropTypes.number),
      departementCode: PropTypes.number,
      id: PropTypes.string,
      isDuo: PropTypes.bool,
      label: PropTypes.string,
      name: PropTypes.string,
      prices: PropTypes.arrayOf(PropTypes.number),
      priceMin: PropTypes.number,
      priceMax: PropTypes.number,
      thumbUrl: PropTypes.string,
    }),
    objectID: PropTypes.string,
  }),
  search: PropTypes.string,
}

export default Result
