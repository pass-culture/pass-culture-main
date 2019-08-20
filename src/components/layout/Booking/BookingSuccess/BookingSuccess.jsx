import React, { Fragment } from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Icon from '../../Icon'
import { getDisplayPrice } from '../../../../helpers'

const BookingSuccess = ({ isEvent, data }) => {
  const token = get(data, 'token').toLowerCase()
  let price = get(data, 'stock.price')
  price = getDisplayPrice(price)
  const onlineOfferUrl = get(data, 'completedUrl')
  const cssclass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked text-center ${cssclass}`}>
      <h3 className="fs22">
        <span
          className="is-block mb12"
          style={{ color: '#27AE60', fontSize: '4.5rem' }}
        >
          <Icon svg="picto-validation" />
        </span>
        <span className="is-block mb36">
          {isEvent && 'Votre réservation est validée.'}
          {!isEvent && (
            <Fragment>
              <span className="is-block">{'Votre pouvez accéder à cette offre'}</span>
              <span className="is-block">{'à tout moment.'}</span>
            </Fragment>
          )}
        </span>
      </h3>
      <p>
        <span className="is-block">
          {price} {'ont été déduits de votre pass.'}
        </span>
        {!onlineOfferUrl && (
          <span className="is-block">{'Présentez le code suivant sur place :'}</span>
        )}
      </p>
      <p className="my28">
        {!onlineOfferUrl && (
          <b
            className="is-block is-size-1"
            data-token={token}
            id="booking-booked-token"
          >
            {token}
          </b>
        )}
        {onlineOfferUrl && (
          <a
            className="is-primary-text is-primary-border px12 py8"
            data-token={token}
            href={onlineOfferUrl}
            id="booking-online-booked-button"
            rel="noopener noreferrer"
            target="_blank"
          >
            <b>{'Accéder à l’offre en ligne'}</b>
          </a>
        )}
      </p>
      <p>
        {!onlineOfferUrl && (
          <Fragment>
            <span className="is-block">{'Retrouvez ce code et les détails de l’offre dans'}</span>
            <span className="is-block">
              {'la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">{'Mes Réservations'}</b>
              </Link>
              {' de votre compte'}
            </span>
          </Fragment>
        )}
        {onlineOfferUrl && (
          <Fragment>
            <span className="is-block">{'Retrouvez l’adresse Internet et les détails de'}</span>
            <span className="is-block">
              {'l’offre dans la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">{'Mes Réservations'}</b>
              </Link>
            </span>
            <span className="is-block">{' de votre compte'}</span>
          </Fragment>
        )}
      </p>
    </div>
  )
}

BookingSuccess.propTypes = {
  data: PropTypes.shape().isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingSuccess
