import classNames from 'classnames'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'

import styles from './Cells.module.scss'
import { DeleteDraftCell } from './DeleteDraftCell'
import { EditOfferCell } from './EditOfferCell'
import { EditStocksCell } from './EditStocksCell'

interface IndividualActionsCellsProps {
  offer: ListOffersOfferResponseModel
  editionOfferLink: string
  editionStockLink: string
}

export const IndividualActionsCells = ({
  offer,
  editionOfferLink,
  editionStockLink,
}: IndividualActionsCellsProps) => {
  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['actions-column']
      )}
    >
      <div className={styles['actions-column-container']}>
        {offer.status === OFFER_STATUS_DRAFT ? (
          <DeleteDraftCell offer={offer} />
        ) : (
          <EditStocksCell offer={offer} editionStockLink={editionStockLink} />
        )}

        <EditOfferCell editionOfferLink={editionOfferLink} />
      </div>
    </td>
  )
}
