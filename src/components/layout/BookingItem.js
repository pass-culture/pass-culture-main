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

import Thumb from './Thumb'
import { getQueryURL } from '../../helpers'
import { THUMBS_URL } from '../../utils/config'
import { getTimezone } from '../../utils/timezone'
import { selectRecommendation } from '../../selectors'

const BookingItem = ({ booking, recommendation }) => {
  const token = get(booking, 'token')
  const offerId = get(booking, 'stock.resolvedOffer.id')
  const mediationId = get(recommendation, 'mediationId')
  const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
  const departementCode = get(
    booking,
    'stock.resolvedOffer.venue.departementCode'
  )
  const tz = getTimezone(departementCode)
  const dateString =
    date &&
    capitalize(
      moment(date)
        .tz(tz)
        .format('dddd DD/MM/YYYY à H:mm')
    )

  const name = get(booking, 'stock.resolvedOffer.eventOrThing.name')
  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `/decouverte/${queryURL}?to=verso`
  const thumbUrl = `${THUMBS_URL}/mediations/${mediationId}`
  const isEvent = (get(recommendation, 'offer.eventId') && true) || false
  const cssclass = (isEvent && 'event') || 'thing'
  const completedUrl = get(recommendation, 'completedUrl')
  return (
    <li className={`booking-item mb16 ${cssclass}`}>
      <Link to={linkURL}>
        <Thumb src={thumbUrl} />
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
  const recommendation = selectRecommendation(state, recommendationId)
  return { recommendation }
})(BookingItem)
