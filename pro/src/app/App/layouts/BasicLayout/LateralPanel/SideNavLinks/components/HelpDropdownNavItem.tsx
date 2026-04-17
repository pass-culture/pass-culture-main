import { HelpDropdownMenu } from '@/app/App/layouts/components/Header/components/HeaderHelpDropdown/HelpDropdownMenu'
import fullHelpIcon from '@/icons/full-help.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HelpDropdownNavItem.module.scss'

interface HelpDropdownNavItemProps {
  isMobileScreen: boolean
}

export const HelpDropdownNavItem = ({
  isMobileScreen,
}: HelpDropdownNavItemProps) => (
  <Dropdown
    title="Centre d’aide"
    side={isMobileScreen ? 'top' : 'right'}
    sideOffset={0}
    trigger={
      // The DS does not allow two icons in the same button
      <button type="button" className={styles['nav-links-help']}>
        <div className={styles['nav-links-help-content']}>
          <SvgIcon src={fullHelpIcon} alt="" width="22" />
          Centre d’aide
        </div>
        <SvgIcon src={fullRightIcon} alt="" width="18" />
      </button>
    }
  >
    <HelpDropdownMenu />
  </Dropdown>
)
