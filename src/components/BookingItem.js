/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import moment from 'moment'
import { capitalize, Icon } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Thumb from './layout/Thumb'
import recommendationSelector from '../selectors/recommendation'
import { getTimezone } from '../utils/timezone'

const BookingItem = ({ booking, recommendation }) => {
  const { stock, token } = booking || {}
  const { offer, offerId } = stock || {}
  const { mediation, mediationId, thumbUrl } = recommendation || {}
  const { eventOrThing, venue } = offer || {}
  const { name } = eventOrThing || {}
  const { departementCode } = venue || {}

  const tz = getTimezone(departementCode)
  const date = get(booking, 'stock.eventOccurrence.beginningDatetime')

  const dateString = capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY à H:mm')
  )
  const mediationQuery = (mediationId && `/${mediationId}`) || ''
  const linkURL = `/decouverte/${offerId}${mediationQuery}`
  return (
    <li className="booking-item">
      <Link to={linkURL}>
        <Thumb src={thumbUrl} withMediation={mediation} />
        <div className="infos">
          <div className="top">
            <h5 title={name}>
              <Dotdotdot clamp={date ? 2 : 3}>{name}</Dotdotdot>
            </h5>
            <span>{dateString}</span>
          </div>
          <div className="token">{token}</div>
        </div>
        <div className="arrow">
          <Icon svg="ico-next-S" className="Suivant" />
        </div>
      </Link>
    </li>
  )
}

BookingItem.defaultProps = {
  booking: null,
  recommendation: null,
}

BookingItem.propTypes = {
  booking: PropTypes.object,
  recommendation: PropTypes.object,
}

export default connect((state, ownProps) => {
  const { recommendationId } = ownProps.booking
  const recommendation = recommendationSelector(state, recommendationId)
  return { recommendation }
})(BookingItem)
