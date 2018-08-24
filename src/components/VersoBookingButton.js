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
    <Link to={`${url}/booking`} className="button is-primary is-go is-medium">
      <Price free="——" value={priceValue} />
      <span>J&apos;y vais!</span>
    </Link>
  )
}

const VersoBookingButton = ({ isReserved, isFinished, url, offer }) => (
  <React.Fragment>
    {isReserved && (
      <Link to="/reservations" className="button is-primary is-go is-medium">
        <Icon name="Check" />
        {'Réservé'}
      </Link>
    )}
    {!isReserved && (
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

VersoBookingButton.defaultProps = {
  offer: null,
}

VersoBookingButton.propTypes = {
  isFinished: PropTypes.bool.isRequired,
  isReserved: PropTypes.bool.isRequired,
  offer: PropTypes.object,
  url: PropTypes.string.isRequired,
}

export default VersoBookingButton
