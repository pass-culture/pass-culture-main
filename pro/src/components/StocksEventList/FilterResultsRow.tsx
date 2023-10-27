import React from 'react'

import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { pluralizeString } from 'utils/pluralize'

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
            {new Intl.NumberFormat('fr-FR').format(resultsCount)}{' '}
            {pluralizeString('occurrence', resultsCount)}
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
