import classNames from 'classnames'

import { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import { SortingMode } from '@/commons/hooks/useColumnSorting'
import { SortArrow } from '@/ui-kit/SortArrow/SortArrow'

import {
  type CellDefinition,
  getCellsDefinition,
} from '../utils/cellDefinitions'
import styles from './OffersTableHead.module.scss'

export type Columns = CellDefinition & {
  isVisuallyHidden?: boolean
  sortableProps?: {
    onColumnHeaderClick: (
      headersName: CollectiveOffersSortingColumn
    ) => SortingMode
    currentSortingColumn: CollectiveOffersSortingColumn | null
    currentSortingMode: SortingMode
  }
}

type OffersTableHeadProps = {
  columns: Columns[]
}

export const OffersTableHead = ({
  columns,
}: OffersTableHeadProps): JSX.Element => {
  return (
    <thead className={styles['offers-thead']}>
      <tr>
        <th id={'offer-head-checkbox'} className={styles['offers-thead-th']}>
          <span className={styles['visually-hidden']}>
            Sélection des offres
          </span>
        </th>
        {columns.map(({ id, title, isVisuallyHidden, sortableProps }) => (
          <th id={id} key={id} className={styles['offers-thead-th']}>
            {isVisuallyHidden ? (
              <span className={styles['visually-hidden']}>{title}</span>
            ) : (
              <>
                {title}
                {sortableProps && (
                  <SortArrow
                    onClick={() => {
                      sortableProps.onColumnHeaderClick(
                        CollectiveOffersSortingColumn.EVENT_DATE
                      )
                    }}
                    sortingMode={
                      sortableProps.currentSortingColumn ===
                      CollectiveOffersSortingColumn.EVENT_DATE
                        ? sortableProps.currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                )}
              </>
            )}
          </th>
        ))}
        <th
          id={getCellsDefinition().ACTIONS.id}
          className={classNames(
            styles['offers-thead-th'],
            styles['offers-thead-th-actions']
          )}
        >
          {getCellsDefinition().ACTIONS.title}
        </th>
      </tr>
    </thead>
  )
}
