import cn from 'classnames'

import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { StatusToggleButton } from 'components/IndividualOffer/Status/StatusToggleButton'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'

import styles from './Status.module.scss'

interface StatusProps {
  offer: GetIndividualOfferResponseModel
}

export const Status = ({ offer }: StatusProps) => {
  // All offer can be manually edited except for:
  // - rejected offers
  // - offers synchronized with a provider
  const canEditPublicationDates =
    offer.status !== OfferStatus.REJECTED && !offer.lastProvider
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
