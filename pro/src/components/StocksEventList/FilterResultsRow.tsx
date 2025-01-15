
import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './FilterResultsRow.module.scss'

interface FilterResultsRowProps {
  colSpan: number
  onFiltersReset: () => void
}

export const FilterResultsRow = ({
  colSpan,
  onFiltersReset,
}: FilterResultsRowProps) => (
  <tr>
    <td colSpan={colSpan}>
      <div className={styles['filtered-data-row']}>
        <Button
          icon={fullRefreshIcon}
          variant={ButtonVariant.TERNARY}
          onClick={onFiltersReset}
        >
          Réinitialiser les filtres
        </Button>
      </div>
    </td>
  </tr>
)
