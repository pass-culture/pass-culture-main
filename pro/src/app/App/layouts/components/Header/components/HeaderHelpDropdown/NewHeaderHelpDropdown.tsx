import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import fullHelpIcon from '@/icons/full-help.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'

export const NewHeaderHelpDropdown = () => (
  <DropdownMenu.Root>
    <DropdownMenu.Trigger asChild>
      <Button
        variant={ButtonVariant.TERNARY}
        className={styles['help-dropdown-trigger']}
      >
        <SvgIcon src={fullHelpIcon} alt="" width="20" />
        <span className={styles['nav-section-title']}>Centre d’aide</span>
        <SvgIcon src={fullRightIcon} alt="" width="18" />
      </Button>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content
      sideOffset={8}
      side="right"
      className={styles['help-dropdown-content']}
    >
      <DropdownMenu.Item asChild>
        <a
          href="https://aide.passculture.app/hc/fr"
          target="_blank"
          rel="noopener noreferrer"
          className={styles['help-dropdown-link']}
        >
          Accéder au centre d’aide
        </a>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
)
