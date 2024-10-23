import strokePageNotFoundIcon from 'icons/stroke-page-not-found.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './IncomeError.module.scss'

export const IncomeError = () => {
  return (
    <div className={styles['income-error']}>
      <SvgIcon
        className={styles['income-error-icon']}
        src={strokePageNotFoundIcon}
        viewBox="0 0 130 100"
        alt=""
        width="100"
      />
      Erreur dans le chargement des données.
    </div>
  )
}
