/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Icon from '../../layout/Icon'
import Thumb from '../../layout/Thumb'
import Ribbon from '../../layout/Ribbon'

const MyBookingItem = ({
  completedUrl,
  cssClass,
  date,
  dateString,
  isCancelled,
  linkURL,
  name,
  thumbUrl,
  timezone,
  token,
}) => (
  <li
    data-token={token}
    data-booked-date={date}
    data-booked-timezone={timezone}
    className={`booking-item mb16 ${cssClass}`}
  >
    {isCancelled && <Ribbon />}
    <Link to={linkURL}>
      {thumbUrl && <Thumb src={thumbUrl} />}
      <div className="infos">
        <div className="top">
          <h5 title={name} className="fs18 is-semi-bold">
            <Dotdotdot clamp={date ? 2 : 3}>{name}</Dotdotdot>
          </h5>
          <span className="fs13">{dateString || 'permanent'}</span>
        </div>
        {!completedUrl && <div className="token">{token}</div>}
      </div>
      <div className="arrow">
        <Icon svg="ico-next-S" className="Suivant" />
      </div>
    </Link>
  </li>
)

MyBookingItem.defaultProps = {
  completedUrl: null,
  date: null,
  dateString: null,
  isCancelled: false,
  name: null,
  thumbUrl: null,
  token: null,
}

MyBookingItem.propTypes = {
  completedUrl: PropTypes.string,
  cssClass: PropTypes.string.isRequired,
  date: PropTypes.string,
  dateString: PropTypes.string,
  isCancelled: PropTypes.bool,
  linkURL: PropTypes.string.isRequired,
  name: PropTypes.string,
  thumbUrl: PropTypes.string,
  timezone: PropTypes.string.isRequired,
  token: PropTypes.string,
}

export default MyBookingItem
