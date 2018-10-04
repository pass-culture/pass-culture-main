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
  const completedUrl = get(data, 'completedUrl')
  // juste pour du debug
  const cssclass = (isEvent && 'event') || 'thing'
  return (
    <div className={`booked has-text-centered ${cssclass}`}>
      <h3 style={{ fontSize: '22px' }}>
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
        {!completedUrl && (
          <span className="is-block">Présentez le code suivant sur place:</span>
        )}
      </p>
      {/* <!-- CODE / LIEN --> */}
      <p className="my28">
        {!completedUrl && <b className="is-block is-size-1">{token}</b>}
        {completedUrl && (
          <a
            className="is-primary-text is-primary-border px12 py8"
            href={completedUrl}
            rel="noopener noreferrer"
            target="_blank"
          >
            <b>Accéder à l&apos;offre en ligne</b>
          </a>
        )}
      </p>
      <p>
        {!completedUrl && (
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
        {completedUrl && (
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
