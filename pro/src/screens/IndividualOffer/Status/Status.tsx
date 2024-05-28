import cn from 'classnames'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import { StatusToggleButton } from 'screens/IndividualOffer/Status/StatusToggleButton'

import styles from './Status.module.scss'

interface StatusProps {
  offerId: number
  status: OfferStatus
  isActive: boolean
  canDeactivate: boolean
}

export const Status = ({
  offerId,
  status,
  isActive,
  canDeactivate,
}: StatusProps) => (
  <div
    className={cn(styles['status'], {
      [styles['multiple-columns']]: canDeactivate,
    })}
    data-testid="status"
  >
    {canDeactivate && (
      <>
        <StatusToggleButton
          offerId={offerId}
          status={status}
          isActive={isActive}
        />
        <div className={styles['separator']} />
      </>
    )}
    <StatusLabel status={status} />
  </div>
)
