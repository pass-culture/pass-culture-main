import cn from 'classnames'

import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import { StatusToggleButton } from '@/components/IndividualOfferLayout/components/Status/StatusToggleButton'
import { StatusLabel } from '@/components/StatusLabel/StatusLabel'

import styles from './Status.module.scss'

interface StatusProps {
  offer: GetIndividualOfferResponseModelV2
  canEditPublicationDates: boolean
}

export const Status = ({ offer, canEditPublicationDates }: StatusProps) => {
  return (
    <div
      className={cn(styles['status'], {
        [styles['multiple-columns']]: canEditPublicationDates,
      })}
      data-testid="status"
    >
      {canEditPublicationDates && (
        <>
          <StatusToggleButton offer={offer} />
          <div className={styles['separator']} />
        </>
      )}
      <StatusLabel status={offer.status} />
    </div>
  )
}
