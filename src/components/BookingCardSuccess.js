/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Icon } from 'antd'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import { getPrice } from '../helpers'

const BookingCardSuccess = ({ isEvent, data }) => {
  const token = get(data, 'token')
  let price = get(data, 'stock.price')
  price = getPrice(price)
  const cssclass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked has-text-centered ${cssclass}`}>
      <h3 style={{ fontSize: '22px' }}>
        <span
          className="is-block mb12"
          style={{ color: '#27AE60', fontSize: '4.5rem' }}
        >
          <Icon type="check-circle" />
        </span>
        <span className="is-block mb36">
          {isEvent
            ? 'Votre réservation est validée.'
            : 'Votre pouvez accéder à cette offfre à tout moment.'}
        </span>
      </h3>
      <p>
        <span className="is-block">{price} ont été déduit de votre pass.</span>
        <span className="is-block">Présentez le code suivant sur place:</span>
      </p>
      <p className="is-size-1 my28">
        <b>{token}</b>
      </p>
      <p>
        Retrouvez ce code et les détails de l&apos;offre dans la rubrique
        <Link to="/reservations">
          <b className="is-primary-text"> Mes Réservations </b>
        </Link>
        de votre compte
      </p>
    </div>
  )
}

BookingCardSuccess.propTypes = {
  data: PropTypes.object.isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingCardSuccess
