/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'

import Icon from '../../layout/Icon'
import { getDisplayPrice } from '../../../helpers'

const BookingCancel = ({ isEvent, data }) => {
  const price = get(data, 'stock.price')
  const formattedPrice = getDisplayPrice(price)
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
        <span className="is-block fs22">Votre réservation est annulée.</span>
      </div>

      <p className="mt40">
        <span className="is-block">
          {formattedPrice} vont être recrédités sur votre pass.
        </span>
        <span className="is-block">
          Vous allez recevoir un e-mail de confirmation.
        </span>
      </p>
    </div>
  )
}

BookingCancel.propTypes = {
  data: PropTypes.object.isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingCancel
