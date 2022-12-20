import cn from 'classnames'
import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'

import styles from './Venue.module.scss'

interface IVenueProps {
  className: string
  venue: GetOffererVenueResponseModel
}

const Venue = ({ className, venue }: IVenueProps) => {
  return (
    <div className={cn(className, styles['venue'])}>
      <div>{venue.name}</div>
      <div>{venue.venueTypeCode}</div>
    </div>
  )
}

export default Venue
