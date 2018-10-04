/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { Icon } from 'pass-culture-shared'

import Price from './Price'
import Finishable from './layout/Finishable'

const renderBookingLink = (url, offer) => {
  const priceValue = get(offer, 'price') || get(offer, 'displayPrice')
  return (
    <Link to={`${url}/booking`} className="button is-primary is-medium">
      <Price free="——" value={priceValue} />
      <span>J&apos;y vais!</span>
    </Link>
  )
}

const VersoBookingButton = ({ booking, isFinished, offer, url }) => {
  const onlineOfferUrl = get(booking, 'completedUrl')
  return (
    <React.Fragment>
      {booking && (
        <React.Fragment>
          {onlineOfferUrl ? (
            <a
              href={`${onlineOfferUrl}`}
              target="_blank"
              rel="noopener noreferrer"
              className="button is-primary is-medium"
            >
              Accéder
            </a>
          ) : (
            <Link to="/reservations" className="button is-primary is-medium">
              <Icon name="Check" />
              Réservé
            </Link>
          )}
        </React.Fragment>
      )}
      {!booking && (
        <React.Fragment>
          {/* FIXME -> décorer avec isFinished/Finishable */}
          {!isFinished && renderBookingLink(url, offer)}
          {isFinished && (
            <Finishable finished>{renderBookingLink(url, offer)}</Finishable>
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  )
}

VersoBookingButton.defaultProps = {
  offer: null,
}

VersoBookingButton.propTypes = {
  booking: PropTypes.object.isRequired,
  isFinished: PropTypes.bool.isRequired,
  offer: PropTypes.object,
  url: PropTypes.string.isRequired,
}

export default VersoBookingButton
