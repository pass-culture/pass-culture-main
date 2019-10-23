import React from 'react'
import PropTypes from 'prop-types'

import Icon from '../../Icon/Icon'
import getDisplayPrice from '../../../../helpers/getDisplayPrice'

const BookingCancel = ({ isEvent, booking }) => {
  const { amount } = booking || {}
  const price = getDisplayPrice(amount)
  const cssClass = isEvent ? 'event' : 'thing'

  return (
    <div className={`text-center ${cssClass}`}>
      <div>
        <span
          className="is-block mt24 mb8"
          style={{ color: '#27AE60', fontSize: '4rem' }}
        >
          <Icon svg="picto-validation" />
        </span>
        <span className="is-block fs22">{'Votre réservation est annulée.'}</span>
      </div>

      <p className="mt40">
        <span className="is-block">{`${price} vont être recrédités sur votre pass.`}</span>
        <span className="is-block">{'Vous allez recevoir un e-mail de confirmation.'}</span>
      </p>
    </div>
  )
}

BookingCancel.propTypes = {
  booking: PropTypes.shape().isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingCancel
