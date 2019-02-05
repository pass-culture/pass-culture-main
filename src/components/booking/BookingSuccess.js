/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Icon } from 'antd'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import { getPrice } from '../../helpers'

const BookingSuccess = ({ isEvent, data }) => {
  const token = get(data, 'token')
  let price = get(data, 'stock.price')
  price = getPrice(price)
  const onlineOfferUrl = get(data, 'completedUrl')
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
          {isEvent && 'Votre réservation est validée.'}
          {!isEvent && (
            <React.Fragment>
              <span className="is-block">
                Votre pouvez accéder à cette offre
              </span>
              <span className="is-block">à tout moment.</span>
            </React.Fragment>
          )}
        </span>
      </h3>
      <p>
        <span className="is-block">{price} ont été déduits de votre pass.</span>
        {!onlineOfferUrl && (
          <span className="is-block">Présentez le code suivant sur place:</span>
        )}
      </p>
      {/* <!-- CODE / LIEN --> */}
      <p className="my28">
        {!onlineOfferUrl && (
          <b
            data-token={token}
            id="booking-booked-token"
            className="is-block is-size-1"
          >
            {token}
          </b>
        )}
        {onlineOfferUrl && (
          <a
            data-token={token}
            id="booking-online-booked-button"
            className="is-primary-text is-primary-border px12 py8"
            href={onlineOfferUrl}
            rel="noopener noreferrer"
            target="_blank"
          >
            <b>Accéder à l&apos;offre en ligne</b>
          </a>
        )}
      </p>
      <p>
        {!onlineOfferUrl && (
          <React.Fragment>
            <span className="is-block">
              Retrouvez ce code et les détails de l&apos;offre dans
            </span>
            <span className="is-block">
              la rubrique
              <Link to="/reservations">
                <b className="is-primary-text"> Mes Réservations </b>
              </Link>
              de votre compte
            </span>
          </React.Fragment>
        )}
        {onlineOfferUrl && (
          <React.Fragment>
            <span className="is-block">
              Retrouvez l&apos;adresse Internet et les détails de
            </span>
            <span className="is-block">
              l&apos;offre dans la rubrique
              <Link to="/reservations">
                <b className="is-primary-text"> Mes Réservations </b>
              </Link>
            </span>
            <span className="is-block">de votre compte</span>
          </React.Fragment>
        )}
      </p>
    </div>
  )
}

BookingSuccess.propTypes = {
  data: PropTypes.object.isRequired,
  isEvent: PropTypes.bool.isRequired,
}

export default BookingSuccess
