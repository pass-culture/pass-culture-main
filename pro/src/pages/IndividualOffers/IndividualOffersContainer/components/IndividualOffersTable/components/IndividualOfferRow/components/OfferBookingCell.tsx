import classNames from 'classnames'

import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import styles from 'styles/components/Cells.module.scss'

interface OfferBookingCellProps {
  rowId: string
  offer: ListOffersOfferResponseModel
}

export const OfferBookingCell = ({ rowId, offer }: OfferBookingCellProps) => {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  console.log(offer)
  const publicationDate =
    offer.status === OfferStatus.ACTIVE ? '21/07/2025 10:00' : null

  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['booking-column']
      )}
      headers={`${rowId} ${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_STATUS.id}`}
    >
      <span
        className={styles['offers-table-cell-mobile-label']}
        aria-hidden={true}
      >
        {`${getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_STATUS.title} :`}
      </span>
    </td>
  )
}
