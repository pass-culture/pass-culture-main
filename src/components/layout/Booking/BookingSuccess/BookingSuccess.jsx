import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

import getDisplayPrice from '../../../../utils/getDisplayPrice'
import Icon from '../../../layout/Icon/Icon'

const BookingSuccess = ({ bookedPayload, isEvent }) => {
  const { quantity, recommendation, stock, token } = bookedPayload
  const url = recommendation ? recommendation.offer.url : null
  const { price } = stock || {}
  const isDuo = quantity === 2
  const cssClass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked text-center ${cssClass}`}>
      <h3 className="fs22">
        <span className="is-block mb12">
          <Icon svg="ico-validation-green" />
        </span>
        <span className="is-block mb36">
          {isEvent && 'Votre réservation '}
          {isEvent && isDuo && <i>
            {'duo '}
          </i>}
          {isEvent && 'est validée.'}
          {!isEvent && (
            <Fragment>
              <span className="is-block">
                {'Votre pouvez accéder à cette offre'}
              </span>
              <span className="is-block">
                {'à tout moment.'}
              </span>
            </Fragment>
          )}
        </span>
      </h3>
      <p>
        <span className="is-block">
          {getDisplayPrice(price * quantity)}
          {' ont été déduits de votre pass.'}
        </span>
        {!url && <span className="is-block">
          {'Présentez le code suivant sur place :'}
        </span>}
      </p>
      <p className="my28">
        {!url && (
          <b
            className="is-block is-size-1 fs48"
            data-token={token.toLowerCase()}
            id="booking-booked-token"
          >
            {token.toLowerCase()}
          </b>
        )}
        {url && (
          <a
            className="is-primary-text is-primary-border px12 py8"
            data-token={token.toLowerCase()}
            href={url}
            id="booking-online-booked-button"
            rel="noopener noreferrer"
            target="_blank"
          >
            <b>
              {'Accéder à l’offre numérique'}
            </b>
          </a>
        )}
      </p>
      <p>
        {!url && (
          <Fragment>
            <span className="is-block">
              {'Retrouvez ce code et les détails de l’offre dans'}
            </span>
            <span className="is-block">
              {'la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">
                  {'Mes Réservations'}
                </b>
              </Link>
              {' de votre compte'}
            </span>
          </Fragment>
        )}
        {url && (
          <Fragment>
            <span className="is-block">
              {'Retrouvez l’adresse Internet et les détails de'}
            </span>
            <span className="is-block">
              {'l’offre dans la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">
                  {'Mes Réservations'}
                </b>
              </Link>
            </span>
            <span className="is-block">
              {' de votre compte'}
            </span>
          </Fragment>
        )}
      </p>
    </div>
  )
}

BookingSuccess.propTypes = {
  bookedPayload: PropTypes.shape({
    quantity: PropTypes.number,
    recommendation: PropTypes.shape({
      offer: PropTypes.shape({
        url: PropTypes.string,
      }).isRequired,
    }).isRequired,
    stock: PropTypes.shape({
      price: PropTypes.number.isRequired,
    }).isRequired,
    token: PropTypes.string.isRequired,
  }).isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingSuccess
