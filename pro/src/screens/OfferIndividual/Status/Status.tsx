import cn from 'classnames'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel'
import StatusToggleButton from 'screens/OfferIndividual/Status/StatusToggleButton'

import styles from './Status.module.scss'

interface IStatus {
  offerId: number
  status: OfferStatus
  isActive: boolean
  canDeactivate: boolean
  reloadOffer: () => void
}

const Status = ({
  offerId,
  status,
  isActive,
  canDeactivate,
  reloadOffer,
}: IStatus) => (
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
          reloadOffer={reloadOffer}
        />
        <div className={styles['separator']} />
      </>
    )}
    <StatusLabel status={status} />
  </div>
)

export default Status
