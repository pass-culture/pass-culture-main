import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { humanizeDate } from '../../../../../../utils/date/date'
import { DEFAULT_THUMB_URL } from '../../../../../../utils/thumb'
import { getTimezone } from '../../../../../../utils/timezone'
import Icon from '../../../../../layout/Icon/Icon'
import Ribbon from '../../../../../layout/Ribbon/Ribbon'

const getDetailsUrl = (offer, location) => `/reservations/details/${offer.id}${location.search}`

const getQrCodeUrl = detailsUrl => `${detailsUrl}/qrcode`

const BookingItem = ({
  booking,
  isQrCodeFeatureDisabled,
  location,
  offer,
  ribbon,
  stock,
  shouldDisplayToken,
  trackConsultOffer,
}) => {
  const { activationCode, completedUrl, qrCode, quantity, token } = booking
  const { beginningDatetime } = stock
  const { label, type } = ribbon || {}
  const { name: offerName, venue, thumbUrl } = offer
  const { departementCode } = venue
  const isDuo = quantity === 2
  const detailsUrl = getDetailsUrl(offer, location)
  const timeZone = getTimezone(departementCode)
  const humanizedDate = beginningDatetime && humanizeDate(beginningDatetime, timeZone)

  return (
    <li
      className="mb-my-booking"
      data-token={token.toLowerCase()}
    >
      <Link
        className="teaser-link"
        onClick={trackConsultOffer}
        to={detailsUrl}
      >
        <div className="teaser-thumb">
          <img
            alt=""
            src={thumbUrl || DEFAULT_THUMB_URL}
          />
        </div>
        <div className="teaser-wrapper">
          <div className="mb-corner bottom left" />
          <div className="mb-corner bottom right" />
          <div className="mb-heading">
            <div className="teaser-title-booking">
              {offerName}
            </div>
            <div className="teaser-sub-title">
              {isDuo && (
                <div className="duo">
                  <span className="duo-logo">
                    {'duo'}
                  </span>
                </div>
              )}
              {humanizedDate || 'Permanent'}
            </div>
          </div>
        </div>
        <div className="teaser-arrow">
          <Icon
            className="teaser-arrow-img"
            svg="ico-next-pink"
          />
        </div>
        {ribbon && (
          <Ribbon
            label={label}
            type={type}
          />
        )}
      </Link>
      {shouldDisplayToken && (
        <div className="mb-token-container">
          <div className="mb-corner top left" />
          <div className="mb-corner top right" />
          <div className="mb-token-title">
            {activationCode ? 'Ton code d’activation' : 'Ta contremarque'}
          </div>
          {isQrCodeFeatureDisabled && (
            <div className="mb-token-contremarque-container">
              <div className="mb-token-flipped">
                {activationCode ? activationCode : token.toLowerCase()}
              </div>
            </div>
          )}
          {!isQrCodeFeatureDisabled && qrCode && (
            <div className="mb-token-contremarque-container">
              <div className="mb-token">
                {activationCode ? activationCode : token.toLowerCase()}
              </div>
              <hr />
              {activationCode ? (
                <div className="mb-token-link-container">
                  <a
                    className="mb-token-link"
                    href={completedUrl}
                    rel="noopener noreferrer"
                    target="_blank"
                    title="Accéder à l’offre - Nouvelle fenêtre"
                  >
                    <Icon
                      className="ico-external-site"
                      svg="ico-external-site-red"
                    />
                    {'Accéder à l’offre'}
                  </a>
                </div>
              ) : (
                <div className="mb-token-link-container">
                  <Link
                    className="mb-token-link"
                    to={getQrCodeUrl(detailsUrl)}
                  >
                    {'Voir le QR code'}
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </li>
  )
}

BookingItem.defaultProps = {
  ribbon: null,
  shouldDisplayToken: true,
}

BookingItem.propTypes = {
  booking: PropTypes.shape({
    id: PropTypes.string,
    activationCode: PropTypes.string,
    qrCode: PropTypes.string,
    completedUrl: PropTypes.string,
    quantity: PropTypes.number,
    token: PropTypes.string.isRequired,
  }).isRequired,
  isQrCodeFeatureDisabled: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  offer: PropTypes.shape({
    name: PropTypes.string.isRequired,
    id: PropTypes.string,
    product: PropTypes.shape({
      name: PropTypes.string,
    }).isRequired,
    venue: PropTypes.shape({
      departementCode: PropTypes.string,
    }).isRequired,
    thumbUrl: PropTypes.string,
  }).isRequired,
  ribbon: PropTypes.shape({
    label: PropTypes.string,
    type: PropTypes.string,
  }),
  shouldDisplayToken: PropTypes.bool,
  stock: PropTypes.shape({
    beginningDatetime: PropTypes.string,
  }).isRequired,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default BookingItem
