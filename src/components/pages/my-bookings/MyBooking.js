import PropTypes from 'prop-types'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Icon from '../../layout/Icon'
import Ribbon from '../../layout/Ribbon'

const MyBooking = ({
  date,
  dateString,
  isCancelled,
  linkURL,
  name,
  thumbUrl,
  timezone,
  token,
  type,
}) => (
  <li
    data-token={token}
    data-booked-date={date}
    data-booked-timezone={timezone}
    data-booked-type={type}
    className="booking-item mb12"
  >
    <Link to={linkURL}>
      <div className="thumb">{thumbUrl && <img alt="" src={thumbUrl} />}</div>
      <div className="infos">
        <div className="top">
          <div className="fs18 is-semi-bold">
            <Dotdotdot clamp={date ? 2 : 3}>{name}</Dotdotdot>
          </div>
          <div className="fs13">{dateString}</div>
        </div>
        {<div className="token">{token.toLowerCase()}</div>}
      </div>
      <div className="arrow">
        {isCancelled && <Ribbon />}
        <Icon svg="ico-next-S" />
      </div>
    </Link>
  </li>
)

MyBooking.defaultProps = {
  date: null,
  dateString: 'Permanent',
  isCancelled: false,
  thumbUrl: null,
}

MyBooking.propTypes = {
  date: PropTypes.string,
  dateString: PropTypes.string,
  isCancelled: PropTypes.bool,
  linkURL: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
  timezone: PropTypes.string.isRequired,
  token: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
}

export default MyBooking
