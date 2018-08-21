/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Icon } from 'antd'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

const renderBookedFooter = () => (
  <p>
    Retrouvez ce code et les détails de l&apos;offre dans la rubrique{' '}
    <Link to="/reservations">Mes Réservations</Link>
    de votre compte
  </p>
)

const BookingCardSuccess = ({ isEvent, price, gratuit }) => {
  const isGratuit = !price || gratuit
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
        {!isGratuit && (
          <span className="is-block">
            {price} ont été déduit de votre pass.
          </span>
        )}
        <span className="is-block">Présentez le code suivant sur place:</span>
      </p>
      <p className="is-size-1">
        <b>A684P6</b>
      </p>
      {renderBookedFooter()}
    </div>
  )
}

BookingCardSuccess.defaultProps = {
  gratuit: false,
  price: null,
}

BookingCardSuccess.propTypes = {
  gratuit: PropTypes.bool,
  isEvent: PropTypes.bool.isRequired,
  price: PropTypes.number,
}

export default BookingCardSuccess
