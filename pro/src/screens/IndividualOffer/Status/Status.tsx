import cn from 'classnames'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import { IndividualOffer } from 'core/Offers/types'
import StatusToggleButton from 'screens/IndividualOffer/Status/StatusToggleButton'

import styles from './Status.module.scss'

interface StatusProps {
  offerId: number
  status: OfferStatus
  isActive: boolean
  canDeactivate: boolean
  setOffer: ((offer: IndividualOffer) => void) | null
}

const Status = ({
  offerId,
  status,
  isActive,
  canDeactivate,
  setOffer,
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
          setOffer={setOffer}
        />
        <div className={styles['separator']} />
      </>
    )}
    <StatusLabel status={status} />
  </div>
)

export default Status
