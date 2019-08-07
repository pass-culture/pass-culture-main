import moment from 'moment'
import PropTypes from 'prop-types'
import React from 'react'
import { capitalize } from 'react-final-form-utils'
import { Link } from 'react-router-dom'

import Icon from '../../../../../layout/Icon'
import Ribbon from '../../../../../layout/Ribbon'
import { getTimezone } from '../../../../../../utils/timezone'

export const stringify = date => timeZone =>
  capitalize(
    moment(date)
      .tz(timeZone)
      .format('dddd DD/MM/YYYY à H:mm')
  )

const getDetailsUrl = (bookingId, location) => {
  const { search } = location

  return `/reservations/details/${bookingId}${search}`
}

const BookingItem = ({ booking, location, offer, ribbon, stock }) => {
  const { id: bookingId, token, thumbUrl } = booking
  const { beginningDatetime } = stock
  const { label, type } = ribbon || {}
  const { product, venue } = offer
  const { name: productName } = product
  const { departementCode } = venue
  const detailsUrl = getDetailsUrl(bookingId, location)
  const timeZone = getTimezone(departementCode)
  const stringifyDate = beginningDatetime && stringify(beginningDatetime)(timeZone)
  return (
    <li
      className="mb-my-booking"
      data-token={token.toLowerCase()}
    >
      <Link
        className="teaser-link"
        to={detailsUrl}
      >
        <div className="teaser-thumb">{thumbUrl && <img
          alt=""
          src={thumbUrl}
                                                   />}
        </div>
        <div className="teaser-wrapper">
          <div className="mb-heading">
            <div className="teaser-title">{productName}</div>
            <div className="teaser-sub-title">{stringifyDate || 'Permanent'}</div>
          </div>
          <div className="mb-token">{token}</div>
        </div>
        <div className="teaser-arrow">
          {ribbon && <Ribbon
            label={label}
            type={type}
                     />}
          <Icon
            className="teaser-arrow-img"
            svg="ico-next-S"
          />
        </div>
      </Link>
    </li>
  )
}

BookingItem.defaultProps = {
  ribbon: null,
}

BookingItem.propTypes = {
  booking: PropTypes.shape({
    id: PropTypes.string,
    thumbUrl: PropTypes.string,
    token: PropTypes.string.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  offer: PropTypes.shape({
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
  stock: PropTypes.shape({
    beginningDatetime: PropTypes.string,
  }).isRequired,
}

export default BookingItem
