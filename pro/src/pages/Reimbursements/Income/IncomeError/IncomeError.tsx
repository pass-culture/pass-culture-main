import strokePageNotFoundIcon from '@/icons/stroke-page-not-found.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IncomeError.module.scss'

export const IncomeError = () => {
  return (
    <p className={styles['income-error']}>
      <SvgIcon
        className={styles['income-error-icon']}
        src={strokePageNotFoundIcon}
        alt=""
      />
      Erreur dans le chargement des données.
    </p>
  )
}
