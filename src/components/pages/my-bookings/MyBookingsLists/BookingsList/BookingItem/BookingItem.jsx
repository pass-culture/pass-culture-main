import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../../../layout/Icon/Icon'
import Ribbon from '../../../../../layout/Ribbon/Ribbon'
import { getTimezone } from '../../../../../../utils/timezone'
import { humanizeDate } from '../../../../../../utils/date/date'
import { DEFAULT_THUMB_URL } from '../../../../../../utils/thumb'
import DuoOfferContainer from '../../../../../layout/DuoOffer/DuoOfferContainer'

const getDetailsUrl = (bookingId, location) => {
  const { pathname, search } = location
  return `${pathname}/details/${bookingId}${search}`
}

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
  const { id: bookingId, qrCode, quantity, token, thumbUrl } = booking
  const { beginningDatetime } = stock
  const { label, type } = ribbon || {}
  const { id: offerId, name: offerName, venue } = offer
  const { departementCode } = venue
  const isDuo = quantity === 2
  const detailsUrl = getDetailsUrl(bookingId, location)
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
              {isDuo && <DuoOfferContainer offerId={offerId} />}
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
        {ribbon && <Ribbon
          label={label}
          type={type}
                   />}
      </Link>
      {shouldDisplayToken && (
        <div className="mb-token-container">
          <div className="mb-corner top left" />
          <div className="mb-corner top right" />
          <div className="mb-token-title">
            {'Votre contremarque'}
          </div>
          {isQrCodeFeatureDisabled && (
            <div className="mb-token-contremarque-container">
              <div className="mb-token-flipped">
                {token.toLowerCase()}
              </div>
            </div>
          )}
          {!isQrCodeFeatureDisabled && qrCode && (
            <div className="mb-token-contremarque-container">
              <div className="mb-token">
                {token.toLowerCase()}
              </div>
              <hr />
              <div className="mb-token-link-container">
                <Link
                  className="mb-token-link"
                  to={getQrCodeUrl(detailsUrl)}
                >
                  {'Voir le QR code'}
                </Link>
              </div>
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
    qrCode: PropTypes.string,
    quantity: PropTypes.number,
    thumbUrl: PropTypes.string,
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
