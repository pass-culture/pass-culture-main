import cn from 'classnames'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { StatusToggleButton } from 'components/IndividualOffer/Status/StatusToggleButton'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'

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
