import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

import getDisplayPrice from '../../../../utils/getDisplayPrice'
import Icon from '../../../layout/Icon/Icon'

const BookingSuccess = ({ quantity, price, token, isEvent, offerUrl }) => {
  const isDuo = quantity === 2
  const cssClass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked text-center ${cssClass}`}>
      <h3 className="fs22">
        <span className="is-block mb12">
          <Icon svg="ico-validation-green" />
        </span>
        <span className="is-block mb36">
          {isEvent && 'Ta réservation '}
          {isEvent && isDuo && (
            <i>
              {'duo '}
            </i>
          )}
          {isEvent && 'est validée.'}
          {!isEvent && (
            <Fragment>
              <span className="is-block">
                {'Tu peux accéder à cette offre '}
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
          {' ont été déduits de ton pass.'}
        </span>
        {!offerUrl && (
          <span className="is-block">
            {'Présente le code suivant sur place :'}
          </span>
        )}
      </p>
      <p className="my28">
        {!offerUrl && (
          <b
            className="is-block is-size-1 fs48"
            data-token={token.toLowerCase()}
            id="booking-booked-token"
          >
            {token.toLowerCase()}
          </b>
        )}
        {offerUrl && (
          <a
            className="is-primary-text is-primary-border px12 py8"
            data-token={token.toLowerCase()}
            href={offerUrl}
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
        {!offerUrl && (
          <Fragment>
            <span className="is-block">
              {'Retrouve ce code et les détails de l’offre dans'}
            </span>
            <span className="is-block">
              {'la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">
                  {'Réservations'}
                </b>
              </Link>
              {' de ton compte'}
            </span>
          </Fragment>
        )}
        {offerUrl && (
          <Fragment>
            <span className="is-block">
              {'Retrouve l’adresse Internet et les détails de'}
            </span>
            <span className="is-block">
              {'l’offre dans la rubrique '}
              <Link to="/reservations">
                <b className="is-primary-text">
                  {'Réservations'}
                </b>
              </Link>
            </span>
            <span className="is-block">
              {' de ton compte'}
            </span>
          </Fragment>
        )}
      </p>
    </div>
  )
}

BookingSuccess.defaultProps = {
  offerUrl: null,
}

BookingSuccess.propTypes = {
  isEvent: PropTypes.bool.isRequired,
  offerUrl: PropTypes.string,
  price: PropTypes.number.isRequired,
  quantity: PropTypes.number.isRequired,
  token: PropTypes.string.isRequired,
}

export default BookingSuccess
