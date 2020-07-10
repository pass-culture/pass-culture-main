import { formatSearchResultDate } from '../../../../../utils/date/date'
import { formatResultPrice } from '../../../../../utils/price'
import { Link } from 'react-router-dom'
import { DEFAULT_THUMB_URL } from '../../../../../utils/thumb'
import React from 'react'
import PropTypes from 'prop-types'

const OfferTile = ({ hit }) => {
  const { offer, venue } = hit
  const offerDates = offer.isEvent ? `${formatSearchResultDate(venue.departementCode, offer.dates)} - ` : ''
  const formattedPrice = formatResultPrice(offer.priceMin, offer.priceMax, offer.isDuo)

  return (
    <li
      className="offer-tile-wrapper"
      key={offer.id}
    >
      <Link to={`/offre/details/${offer.id}`}>
        <div className="otw-image-wrapper">
          <img
            alt=""
            src={offer.thumbUrl ? offer.thumbUrl : DEFAULT_THUMB_URL}
          />
        </div>
        <p className="otw-venue">
          {venue.name}
        </p>
        <p className="otw-offer-info">
          <span>
            {offerDates}
          </span>
          <span>
            {formattedPrice}
          </span>
        </p>
      </Link>
    </li>
  )
}

OfferTile.propTypes = {
  hit: PropTypes.shape().isRequired
}

export default OfferTile
