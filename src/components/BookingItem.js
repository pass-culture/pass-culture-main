import get from 'lodash.get'
import moment from 'moment'
import { capitalize } from 'pass-culture-shared'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import getTimezone from '../getters/timezone'
import Icon from './layout/Icon'
import Thumb from './layout/Thumb'
import { getDiscoveryPath } from '../utils/getDiscoveryPath'

const BookingItem = ({ booking }) => {
  const {
    mediation,
    mediationId,
    offer,
    offerId,
    thumbUrl,
    token
  } = (booking || {})
  const {
    eventOccurence,
    eventOrThing,
    venue
  } = (offer || {})
  const {
    name
  } = (eventOrThing || {})
  const tz = getTimezone(venue)
  const date = get(eventOccurence, 'beginningDatetime')
  return (
    <li className="booking-item">
      <Link to={`/decouverte/${offerId}/${mediationId}?onVerso`}>
        <Thumb src={thumbUrl} withMediation={mediation} />
        <div className="infos">
          <div className="top">
            <h5 title={name}>
              <Dotdotdot clamp={date ? 2 : 3}>
                {name}
              </Dotdotdot>
            </h5>
            <span>
              {
                capitalize(
                  moment(date)
                    .tz(tz)
                    .format('dddd DD/MM/YYYY à H:mm')
                )
              }
            </span>
          </div>
          <div className="token">
            {token}
          </div>
        </div>
        <div className="arrow">
          <Icon svg="ico-next-S" className="Suivant" />
        </div>
      </Link>
    </li>
  )
}

export default BookingItem
