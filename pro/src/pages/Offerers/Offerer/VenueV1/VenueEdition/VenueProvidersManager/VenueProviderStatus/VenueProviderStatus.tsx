import React from 'react'

import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'

import styles from './VenueProviderStatus.module.scss'

interface VenueProviderStatusProps {
  isActive: boolean
}

const VenueProviderStatus = ({
  isActive,
}: VenueProviderStatusProps): JSX.Element => {
  const statusClassName = isActive ? 'status-active' : 'status-inactive'
  return (
    <span className={`${styles['venue-provider-status']} ${statusClassName}`}>
      {isActive ? (
        <>
          <StatusValidatedIcon />
          Synchronisation activée
        </>
      ) : (
        <>
          <StatusInactiveIcon />
          Synchronisation en pause
        </>
      )}
    </span>
  )
}

export default VenueProviderStatus
