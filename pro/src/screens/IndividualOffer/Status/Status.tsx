import cn from 'classnames'
import React from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import { StatusToggleButton } from 'screens/IndividualOffer/Status/StatusToggleButton'

import styles from './Status.module.scss'

interface StatusProps {
  offer: GetIndividualOfferResponseModel
}

export const Status = ({ offer }: StatusProps) => (
  <div
    className={cn(styles['status'], {
      [styles['multiple-columns']]: offer.isActivable,
    })}
    data-testid="status"
  >
    {offer.isActivable && (
      <>
        <StatusToggleButton offer={offer} />
        <div className={styles['separator']} />
      </>
    )}
    <StatusLabel status={offer.status} />
  </div>
)
