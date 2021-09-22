import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { formatSearchResultDate } from '../../../../../../utils/date/date'
import { humanizeId } from '../../../../../../utils/dehumanizeId/dehumanizeId'
import { getHumanizeRelativeDistance } from '../../../../../../utils/geolocation'
import getThumbUrl from '../../../../../../utils/getThumbUrl'
import { formatResultPrice } from '../../../../../../utils/price'
import { DEFAULT_THUMB_URL } from '../../../../../../utils/thumb'

const Result = ({ result, geolocation, search, searchGroupLabel }) => {
  const { _geoloc = {}, objectID, offer, venue } = result
  const { dates, isDigital, isDuo, name, priceMin, priceMax, thumbUrl } = offer
  const { latitude: userLatitude, longitude: userLongitude } = geolocation
  const { lat: venueLatitude, lng: venueLongitude } = _geoloc
  const { departementCode } = venue || {}
  const thumbSrc = thumbUrl !== null ? getThumbUrl(thumbUrl) : DEFAULT_THUMB_URL
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
      to={`/recherche/resultats/details/${humanizeId(objectID)}${search}`}
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
            {!isDigital && geolocation && humanizedDistance && (
              <span
                className="result-distance"
                data-test="result-distance-test"
              >
                {humanizedDistance}
              </span>
            )}
          </div>
          <p className="result-type">
            {searchGroupLabel}
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
  searchGroupLabel: '',
}

Result.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  result: PropTypes.shape({
    offer: PropTypes.shape({
      dates: PropTypes.arrayOf(PropTypes.number),
      isDigital: PropTypes.bool,
      isDuo: PropTypes.bool,
      isEvent: PropTypes.bool,
      label: PropTypes.string,
      name: PropTypes.string,
      priceMin: PropTypes.number,
      priceMax: PropTypes.number,
      thumbUrl: PropTypes.string,
    }),
    _geoloc: PropTypes.shape({
      lat: PropTypes.number,
      lng: PropTypes.number,
    }),
    venue: PropTypes.shape({
      departmentCode: PropTypes.string,
      name: PropTypes.string,
      publicName: PropTypes.string,
    }),
    objectID: PropTypes.string.isRequired,
  }),
  search: PropTypes.string,
  searchGroupLabel: PropTypes.string,
}

export default Result
