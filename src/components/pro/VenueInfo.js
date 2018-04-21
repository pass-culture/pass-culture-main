import React from 'react'

import withFrontendVenue from '../hocs/withFrontendVenue'
import { navigationLink } from '../../utils/geolocation'

const VenueInfo = ({
  address,
  description,
  thumbCount,
  name,
  latitude,
  longitude,
  thumbUrl,
}) => {
  return (
    <div className="venue-info">
      <img alt="" className="venue-picture" src={thumbUrl} />
      <h3>{name}</h3>
      {description}
      <a href={navigationLink(latitude, longitude)}>
        {address &&
          address.split('\n').map((a, index) => <p key={index}>{a}</p>)}
      </a>
      <div className="clearfix" />
    </div>
  )
}

export default withFrontendVenue(VenueInfo)
