import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { formatSearchResultDate } from '../../../../../../utils/date/date'
import { formatResultPrice } from '../../../../../../utils/price'
import { DEFAULT_THUMB_URL } from '../../../../../../utils/thumb'
import getThumbUrl from '../../../../../../utils/getThumbUrl'
import { PANE_LAYOUT } from '../../domain/layout'
import { formatToReadableString } from '../../../../../../utils/strings/formatToReadableString'
import { SearchHit } from '../../../../search/Results/utils'

export const noOp = () => false

const preventDefault = event => {
  event.preventDefault()
}

const OfferTile = ({ historyPush, hit, isSwitching, layout, trackConsultOffer, moduleName }) => {
  const { offer, venue } = hit
  const offerDates = offer.isEvent
    ? `${formatSearchResultDate(venue.departementCode, offer.dates)}${
        layout === PANE_LAYOUT['ONE-ITEM-MEDIUM'] ? ' - ' : ''
      }`
    : ''

  const prices = offer.prices || []
  const priceMax = Math.max(...prices)
  const priceMin = Math.min(...prices)
  const formattedPrice = formatResultPrice(priceMin, priceMax, offer.isDuo)

  function goToOffer(event) {
    if (!isSwitching) {
      trackConsultOffer(offer.id)
      historyPush({
        pathname: `/accueil/details/${offer.id}`,
        state: { moduleName },
      })
    }
    event.preventDefault()
  }

  return (
    <li
      className="offer-tile-wrapper"
      key={offer.id}
    >
      <Link
        onClick={goToOffer}
        onMouseDown={preventDefault}
        to={noOp}
      >
        <div className="otw-image-wrapper">
          <img
            alt=""
            src={offer.thumbUrl ? getThumbUrl(offer.thumbUrl) : DEFAULT_THUMB_URL}
          />
          <div className="otw-offer-linear-background">
            <div className="otw-offer-name">
              {offer.name}
            </div>
          </div>
        </div>
        <p className="otw-venue">
          {venue.publicName || formatToReadableString(venue.name)}
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

OfferTile.defaultProps = {
  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
}

OfferTile.propTypes = {
  historyPush: PropTypes.func.isRequired,
  hit: PropTypes.shape(SearchHit).isRequired,
  isSwitching: PropTypes.bool.isRequired,
  layout: PropTypes.string,
  moduleName: PropTypes.string.isRequired,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default OfferTile
