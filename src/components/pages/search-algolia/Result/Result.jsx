import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import React from 'react'

import { formatResultDate } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import { DEFAULT_THUMB_URL } from '../../../../utils/thumb'

const Result = ({ result, geolocation, search }) => {
  const { _geoloc = {}, objectID, offer } = result
  const { dates, departementCode, id: offerId, label, name, priceMin, priceMax, thumbUrl } = offer
  const { latitude: userLatitude, longitude: userLongitude } = geolocation
  const { lat: venueLatitude, lng: venueLongitude } = _geoloc
  const thumbSrc = thumbUrl !== null ? thumbUrl : DEFAULT_THUMB_URL
  const formattedDate = formatResultDate(departementCode, dates)
  const priceLabel = priceMin === 0 ? 'Gratuit' : priceMin === priceMax ? `${priceMin} €` : `A partir de ${priceMin} €`

  return (
    <Link
      key={objectID}
      to={`/recherche-offres/resultats/details/${offerId}${search}`}
    >
      <div className="result">
        <div className="result-wrapper">
          <img
            alt=""
            className="result-image"
            src={thumbSrc}
          />
          <p className="result-container">
            <h1 className="result-title">
              {name}
            </h1>
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
            <p className="result-price">
              {priceLabel}
            </p>
          </p>
        </div>
        <div className="result-distance">
          {getHumanizeRelativeDistance(
            userLatitude,
            userLongitude,
            venueLatitude,
            venueLongitude
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
