import classNames from 'classnames'

import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import { SortingMode } from 'commons/hooks/useColumnSorting'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import { CellDefinition, CELLS_DEFINITIONS } from '../utils/cellDefinitions'

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
  areAllOffersSelected: boolean
  isAtLeastOneOfferChecked: boolean
  toggleSelectAllCheckboxes: () => void
  columns: Columns[]
}

export const OffersTableHead = ({
  areAllOffersSelected,
  isAtLeastOneOfferChecked,
  toggleSelectAllCheckboxes,
  columns,
}: OffersTableHeadProps): JSX.Element => {
  return (
    <thead role="rowgroup" className={styles['offers-thead']}>
      <tr>
        <th
          id={CELLS_DEFINITIONS.CHECKBOX.id}
          role="columnheader"
          className={classNames(
            styles['offers-thead-th'],
            styles['offers-thead-th-checkbox']
          )}
        >
          <div className={styles['offers-thead-th-checkbox-wrapper']}>
            <BaseCheckbox
              exceptionnallyHideLabelDespiteA11y
              checked={areAllOffersSelected}
              partialCheck={!areAllOffersSelected && isAtLeastOneOfferChecked}
              onChange={toggleSelectAllCheckboxes}
              label={
                areAllOffersSelected
                  ? 'Tout désélectionner'
                  : 'Tout sélectionner'
              }
            />
          </div>
        </th>
        {columns.map(
          ({ id, title, isVisuallyHidden, sortableProps }, index) => (
            <th
              id={id}
              key={index}
              role="columnheader"
              className={styles['offers-thead-th']}
            >
              {isVisuallyHidden ? (
                <span className={styles['visually-hidden']}>{title}</span>
              ) : (
                <>
                  {title}
                  {sortableProps && (
                    <>
                      {' '}
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
                    </>
                  )}
                </>
              )}
            </th>
          )
        )}
        <th
          id={CELLS_DEFINITIONS.ACTIONS.id}
          role="columnheader"
          className={classNames(
            styles['offers-thead-th'],
            styles['offers-thead-th-actions']
          )}
        >
          {CELLS_DEFINITIONS.ACTIONS.title}
        </th>
      </tr>
    </thead>
  )
}
