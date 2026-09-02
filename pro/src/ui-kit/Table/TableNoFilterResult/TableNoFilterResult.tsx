import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefresh from '@/icons/full-refresh.svg'
import strokeSearchIcon from '@/icons/stroke-search-2.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './TableNoFilterResult.module.scss'

interface NoResultsProps {
  colSpan: number
  message: string
  subtitle?: string
  resetMessage?: string
  resetFilters: () => void
  hasNoResult?: boolean
}

export const TableNoFilterResult = ({
  colSpan = 1,
  message = 'Pas de résultat pour votre recherche',
  subtitle = 'Vous pouvez modifier votre recherche ou',
  resetMessage = 'Réinitialiser les filtres',
  resetFilters,
  hasNoResult = false,
}: NoResultsProps): JSX.Element => (
  <tr>
    <td colSpan={colSpan} role="status">
      {hasNoResult ? (
        <div className={styles['search-no-results']}>
          <SvgIcon
            src={strokeSearchIcon}
            alt=""
            className={styles['search-no-results-icon']}
            width="80"
            aria-hidden={true}
          />
          <p className={styles['search-no-results-title']}>{message}</p>
          <p className={styles['search-no-results-subtitle']}>{subtitle}</p>
          <div className={styles['search-no-results-cta']}>
            <Button
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullRefresh}
              onClick={resetFilters}
              label={resetMessage}
            />
          </div>
        </div>
      ) : (
        <span>&nbsp;</span>
      )}
    </td>
  </tr>
)
