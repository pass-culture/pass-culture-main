import get from 'lodash.get'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'
import moment from 'moment'

import getTimezone from '../getters/timezone'
import getVenue from '../getters/venue'
import Icon from './layout/Icon'
import Thumb from './layout/Thumb'
import Capitalize from './utils/Capitalize'
import { getDiscoveryPath } from '../utils/getDiscoveryPath'

const BookingItem = props => {
  const { mediation, offer, thumbUrl, token } = props
  const venue = getVenue(null, offer)
  const tz = getTimezone(venue)
  const date = get(offer, 'eventOccurence.beginningDatetime')
  return (
    <li className="booking-item">
      <Link to={`${getDiscoveryPath(offer, mediation, true)}`}>
        <Thumb src={thumbUrl} withMediation={mediation} />
        <div className="infos">
          <div className="top">
            <h5 title={get(props, 'source.name')}>
              <Dotdotdot clamp={date ? 2 : 3}>
                {get(props, 'source.name')}
              </Dotdotdot>
            </h5>
            <Capitalize>
              {moment(date)
                .tz(tz)
                .format('dddd DD/MM/YYYY à H:mm')}
            </Capitalize>
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
