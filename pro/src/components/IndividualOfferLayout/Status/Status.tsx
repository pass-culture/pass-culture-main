import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import cn from 'classnames'
import { StatusToggleButton } from 'components/IndividualOfferLayout/Status/StatusToggleButton'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'

import styles from './Status.module.scss'

interface StatusProps {
  offer: GetIndividualOfferResponseModel
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
