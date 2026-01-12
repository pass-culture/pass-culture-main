import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import { HelpDropdownMenu } from '@/app/App/layouts/components/Header/components/HeaderHelpDropdown/HelpDropdownMenu'
import fullHelpIcon from '@/icons/full-help.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'

interface HelpDropdownNavItemProps {
  isMobileScreen: boolean
}

export const HelpDropdownNavItem = ({
  isMobileScreen,
}: HelpDropdownNavItemProps) => (
  <div>
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant={ButtonVariant.TERNARY}
          className={styles['nav-links-item']}
        >
          <SvgIcon src={fullHelpIcon} alt="" width="18" />
          <span className={styles['nav-section-title']}>Centre d’aide</span>
          <SvgIcon src={fullRightIcon} alt="" width="18" />
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content
        side={isMobileScreen ? 'top' : 'right'}
        className={styles['help-dropdown-content']}
      >
        <HelpDropdownMenu />
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
)
