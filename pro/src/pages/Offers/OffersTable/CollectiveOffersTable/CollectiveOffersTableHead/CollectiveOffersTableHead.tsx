import classNames from 'classnames'

import { SortArrow } from 'components/StocksEventList/SortArrow'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { SortingMode } from 'hooks/useColumnSorting'

import { CollectiveOffersSortingColumn } from '../CollectiveOffersTable'

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
  return (
    <thead className={styles['collective-offers-thead']}>
      <tr>
        <th className={styles['offer-reference-th']} />
        <th
          id="collective-offer-head-checkbox"
          className={styles['collective-th']}
        >
          <span className="visually-hidden">Case à cocher</span>
        </th>
        {isCollectiveOffersExpirationEnabled && (
          <th
            id="collective-offer-head-expiration"
            className={styles['expiration-date-th']}
          >
            <span className="visually-hidden">
              Information sur l’expiration
            </span>
          </th>
        )}
        <th id="collective-offer-head-image">
          <span className="visually-hidden">Image</span>
        </th>
        <th
          id="collective-offer-head-name"
          className={classNames(styles['collective-th-width'])}
        >
          <span className="visually-hidden">Nom</span>
        </th>
        {isCollectiveOffersExpirationEnabled && (
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
        )}

        <th
          id="collective-offer-head-venue"
          className={classNames(
            styles['collective-th'],
            styles['collective-th-width']
          )}
        >
          Lieu
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
