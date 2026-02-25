import classnames from 'classnames'

import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavToggleButton.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavToggleButtonProps {
  icon: string
  title: string
  isExpanded: boolean
  onClick: () => void
  ariaControls: string
  id: string
}

export const SideNavToggleButton = ({
  icon,
  title,
  isExpanded,
  onClick,
  ariaControls,
  id,
}: SideNavToggleButtonProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={classnames(styles['nav-links-item'])}
      aria-expanded={Boolean(isExpanded)}
      aria-controls={ariaControls}
      id={id}
    >
      <SvgIcon src={icon} alt="" width={NAV_ITEM_ICON_SIZE} />
      <span className={styles['nav-section-title']}>{title}</span>
      <SvgIcon src={isExpanded ? fullUpIcon : fullDownIcon} alt="" width="18" />
    </button>
  )
}
