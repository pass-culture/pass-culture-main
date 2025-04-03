import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InvoicesNoResult.module.scss'

interface InvoicesNoResultsProps {
  areFiltersDefault: boolean
  onReset: () => void
}

export const InvoicesNoResult = ({
  areFiltersDefault,
  onReset,
}: InvoicesNoResultsProps): JSX.Element => {
  return (
    <div className={styles['no-refunds']}>
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className={styles['no-refunds-icon']}
        width="124"
      />
      <p className={styles['no-refunds-title']}>
        Aucun justificatif de remboursement trouvé pour votre recherche
      </p>
      <p className={styles['no-refunds-description']}>
        Vous pouvez modifier votre recherche ou
        <br />
        <Button
          disabled={areFiltersDefault}
          onClick={onReset}
          variant={ButtonVariant.TERNARYBRAND}
          icon={fullRefreshIcon}
        >
          Réinitialiser les filtres
        </Button>
      </p>
    </div>
  )
}
