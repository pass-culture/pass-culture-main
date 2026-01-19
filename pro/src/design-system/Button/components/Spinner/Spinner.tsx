import loadingIcon from '@/icons/stroke-pass.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Spinner.module.scss'

export const Spinner = () => {
  return (
    <div className={styles['spinner-icon']} data-testid="spinner">
      <SvgIcon
        src={loadingIcon}
        alt=""
        width={'16'}
        className={styles['spinner-svg']}
        data-testid="spinner-svg"
      />
    </div>
  )
}
