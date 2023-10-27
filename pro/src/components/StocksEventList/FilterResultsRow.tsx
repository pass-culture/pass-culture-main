import React from 'react'

import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './FilterResultsRow.module.scss'

interface FilterResultsRowProps {
  colSpan: number
  onFiltersReset: () => void
  resultsCount: number
}

export const FilterResultsRow = ({
  colSpan,
  onFiltersReset,
  resultsCount,
}: FilterResultsRowProps) => (
  <tr>
    <td colSpan={colSpan}>
      <div className={styles['filtered-data-row']}>
        <div>
          Résultat de recherche :{' '}
          <span className={styles['search-result']}>
            {resultsCount} occurrence
            {resultsCount !== 1 && 's'}
          </span>
        </div>

        <div>
          <Button
            icon={fullRefreshIcon}
            variant={ButtonVariant.TERNARY}
            onClick={onFiltersReset}
          >
            Réinitialiser les filtres
          </Button>
        </div>
      </div>
    </td>
  </tr>
)
