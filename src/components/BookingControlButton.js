/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { Icon } from 'pass-culture-shared'

import Price from './Price'
import Finishable from './layout/Finishable'

const renderAlreadyBookedLink = () => (
  <Link to="/reservations" className="button is-primary is-go is-medium">
    <Icon name="Check" />
    {'Réservé'}
  </Link>
)

const renderBookingLink = (matchURL, offer) => {
  const priceValue = get(offer, 'price') || get(offer, 'displayPrice')
  return (
    <Link
      to={`${matchURL}/booking`}
      className="button is-primary is-go is-medium"
    >
      <Price free="——" value={priceValue} />
      <span>J&apos;y vais!</span>
    </Link>
  )
}

const VersoBookingButton = ({
  isAlreadyBooked,
  isFinished,
  matchURL,
  offer,
}) => (
  <React.Fragment>
    {isAlreadyBooked && renderAlreadyBookedLink()}
    {!isAlreadyBooked && (
      <React.Fragment>
        {/* FIXME -> décorer avec isFinished/Finishable */}
        {!isFinished && renderBookingLink(matchURL, offer)}
        {isFinished && (
          <Finishable finished>{renderBookingLink(matchURL, offer)}</Finishable>
        )}
      </React.Fragment>
    )}
  </React.Fragment>
)

VersoBookingButton.defaultProps = {
  offer: null,
}

VersoBookingButton.propTypes = {
  isAlreadyBooked: PropTypes.bool.isRequired,
  isFinished: PropTypes.bool.isRequired,
  matchURL: PropTypes.string.isRequired,
  offer: PropTypes.object,
}

export default VersoBookingButton
