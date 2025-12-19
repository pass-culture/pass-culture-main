import loadingIcon from '@/icons/stroke-pass.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { ButtonSize } from '../../types'
import { ICON_WIDTH } from '../../utils/constants'
import styles from './Spinner.module.scss'

export interface SpinnerProps {
  size?: ButtonSize
}

export const Spinner = ({ size = ButtonSize.DEFAULT }: SpinnerProps) => {
  return (
    <div className={styles['spinner-icon']} data-testid="spinner">
      <SvgIcon
        src={loadingIcon}
        alt=""
        width={ICON_WIDTH[size]}
        className={styles['spinner-svg']}
        data-testid="spinner-svg"
      />
    </div>
  )
}
