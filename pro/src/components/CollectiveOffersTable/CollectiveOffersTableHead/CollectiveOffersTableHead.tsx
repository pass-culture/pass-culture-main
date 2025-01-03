import classNames from 'classnames'

import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { SortingMode } from 'commons/hooks/useColumnSorting'
import { SortArrow } from 'components/StocksEventList/SortArrow'

import styles from './CollectiveOffersTableHead.module.scss'

type CollectiveOffersTableHeadProps = {
  onColumnHeaderClick: (
    headersName: CollectiveOffersSortingColumn
  ) => SortingMode
  currentSortingColumn: CollectiveOffersSortingColumn | null
  currentSortingMode: SortingMode
}

export const CollectiveOffersTableHead = ({
  onColumnHeaderClick,
  currentSortingColumn,
  currentSortingMode,
}: CollectiveOffersTableHeadProps): JSX.Element => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  return (
    <thead className={styles['collective-offers-thead']}>
      <tr>
        <th className={styles['offer-reference-th']} />
        <th
          id="collective-offer-head-checkbox"
          className={styles['collective-th']}
        >
          <span className={styles['visually-hidden']}>Case à cocher</span>
        </th>
        <th
          id="collective-offer-head-expiration"
          className={styles['expiration-date-th']}
        >
          <span className={styles['visually-hidden']}>
            Information sur l’expiration
          </span>
        </th>
        <th id="collective-offer-head-image">
          <span className={styles['visually-hidden']}>Image</span>
        </th>
        <th
          id="collective-offer-head-name"
          className={classNames(styles['collective-th-width'])}
        >
          <span className={styles['visually-hidden']}>Nom</span>
        </th>
        <th
          id="collective-offer-head-event-date"
          className={styles['collective-th']}
        >
          Date de l’évènement{' '}
          <SortArrow
            onClick={() => {
              onColumnHeaderClick(CollectiveOffersSortingColumn.EVENT_DATE)
            }}
            sortingMode={
              currentSortingColumn ===
              CollectiveOffersSortingColumn.EVENT_DATE
                ? currentSortingMode
                : SortingMode.NONE
            }
          />
        </th>

        <th
          id="collective-offer-head-venue"
          className={classNames(
            styles['collective-th'],
            styles['collective-th-width']
          )}
        >
          {isOfferAddressEnabled ? 'Structure' : 'Lieu'}
        </th>
        <th
          id="collective-offer-head-institution"
          className={styles['collective-th']}
        >
          Établissement
        </th>
        <th
          id="collective-offer-head-status"
          className={styles['collective-th']}
        >
          Statut
        </th>
        <th
          className={classNames(
            styles['collective-th'],
            styles['collective-th-actions']
          )}
          id="collective-offer-head-actions"
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
