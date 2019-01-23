/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Icon } from 'antd'
import get from 'lodash.get'
import PropTypes from 'prop-types'

import { getPrice } from '../../helpers'

const BookingCancel = ({ isEvent, data }) => {
  let price = get(data, 'stock.price')
  price = getPrice(price)
  // juste pour du debug
  const cssclass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked text-center ${cssclass}`}>
      <h3 className="fs22">
        {/* <!-- ICON --> */}
        <span
          className="is-block mb12"
          style={{ color: '#27AE60', fontSize: '4.5rem' }}
        >
          <Icon type="check-circle" />
        </span>
        <span className="is-block mb36">
          <span className="is-block">Votre réservation est annulée.</span>
        </span>
      </h3>
      <p>
        <span className="is-block">
          {price} vont être recrédités sur votre pass.
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
