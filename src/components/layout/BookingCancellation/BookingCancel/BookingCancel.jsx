import React from 'react'
import PropTypes from 'prop-types'

import Icon from '../../../layout/Icon/Icon'
import getDisplayPrice from '../../../../utils/getDisplayPrice'

const BookingCancel = ({ isEvent, booking }) => {
  const { amount, quantity } = booking || {}
  const price = getDisplayPrice(amount * quantity)
  const cssClass = isEvent ? 'event' : 'thing'

  return (
    <div className={`text-center ${cssClass}`}>
      <div>
        <span className="is-block mt24 mb8">
          <Icon svg="picto-validation" />
        </span>
        <span className="is-block fs22">
          {'Votre réservation est annulée.'}
        </span>
      </div>

      <p className="mt40">
        <span className="is-block">
          {`${price} vont être recrédités sur votre pass.`}
        </span>
        <span className="is-block">
          {'Vous allez recevoir un e-mail de confirmation.'}
        </span>
      </p>
    </div>
  )
}

BookingCancel.propTypes = {
  booking: PropTypes.shape().isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingCancel
