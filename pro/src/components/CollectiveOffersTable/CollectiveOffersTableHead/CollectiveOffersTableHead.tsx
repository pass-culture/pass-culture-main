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
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  return (
    <thead className={styles['collective-offers-thead']}>
      <tr>
        <th className={styles['collective-th']}>
          <span className={styles['visually-hidden']}>Case à cocher</span>
        </th>
        <th className={styles['collective-th']}>
          <span className={styles['visually-hidden']}>Image</span>
        </th>
        <th className={classNames(styles['collective-th-width'])}>
          <span className={styles['visually-hidden']}>Nom</span>
        </th>
        {isCollectiveOffersExpirationEnabled && (
          <th className={styles['collective-th']}>
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
        )}

        <th
          className={classNames(
            styles['collective-th'],
            styles['collective-th-width']
          )}
        >
          {isOfferAddressEnabled ? 'Structure' : 'Lieu'}
        </th>
        <th className={styles['collective-th']}>Établissement</th>
        <th className={styles['collective-th']}>Statut</th>
        <th
          className={classNames(
            styles['collective-th'],
            styles['collective-th-actions']
          )}
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
