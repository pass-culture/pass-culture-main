import fullRefresh from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './TableNoFilterResult.module.scss'

interface NoResultsProps {
  colSpan: number
  message: string
  resetFilters: () => void
}

export const TableNoFilterResult = ({
  colSpan = 1,
  message = 'Pas de résultat pour votre recherche',
  resetFilters,
}: NoResultsProps): JSX.Element => (
  <tr>
    <td colSpan={colSpan}>
      <div className={styles['search-no-results']}>
        <SvgIcon
          src={strokeSearchIcon}
          alt="Illustration de recherche"
          className={styles['search-no-results-icon']}
          width="124"
        />
        <p className={styles['search-no-results-title4']}>{message}</p>
        <p className={styles['search-no-results-text']}>
          Vous pouvez modifier votre recherche ou
        </p>
        <Button
          variant={ButtonVariant.TERNARYBRAND}
          icon={fullRefresh}
          onClick={resetFilters}
        >
          Réinitialiser les filtres
        </Button>
      </div>
    </td>
  </tr>
)
