import cn from 'classnames'
import React from 'react'

import { IOfferer } from 'core/Offerers/types'
import { Title } from 'ui-kit'

import styles from './Offerer.module.scss'
import { Venue } from './Venue'

interface IOffererProps {
  className: string
  offerer: IOfferer
}

const Offerer = ({ className, offerer }: IOffererProps) => {
  return (
    <div className={cn(className, styles['offerer'])}>
      <Title level={4}>{offerer.name}</Title>
      <div className={styles['venue-list']}>
        {offerer.managedVenues.map(venue => (
          <Venue venue={venue} className={styles['venue-list-item']} />
        ))}
      </div>
    </div>
  )
}

export default Offerer
