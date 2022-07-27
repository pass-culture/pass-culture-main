import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './VenueProviderStatus.module.scss'

export interface VenueProviderStatusProps {
  isActive: boolean
}

const VenueProviderStatus = ({
  isActive,
}: VenueProviderStatusProps): JSX.Element => {
  const statusClassName = isActive ? 'status-active' : 'status-inactive'
  const statusIcon = isActive ? 'ico-status-validated' : 'ico-status-inactive'
  return (
    <span className={`${styles['venue-provider-status']} ${statusClassName}`}>
      <Icon svg={statusIcon} />
      {isActive ? 'Synchronisation activée' : 'Synchronisation en pause'}
    </span>
  )
}

export default VenueProviderStatus
