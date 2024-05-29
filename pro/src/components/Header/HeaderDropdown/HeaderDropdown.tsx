import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useSelector } from 'react-redux'

import { useAnalytics } from 'app/App/analytics/firebase'
import { HelpDropdownMenu } from 'components/Header/HeaderHelpDropdown/HelpDropdownMenu'
import { Events } from 'core/FirebaseEvents/constants'
import fullCloseIcon from 'icons/full-close.svg'
import fullLogoutIcon from 'icons/full-logout.svg'
import fullProfilIcon from 'icons/full-profil.svg'
import { selectCurrentUser } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HeaderDropdown.module.scss'

export const HeaderDropdown = () => {
  const { logEvent } = useAnalytics()
  const currentUser = useSelector(selectCurrentUser)
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className={cn(styles['dropdown-button'])} title="Profil">
          <SvgIcon src={fullProfilIcon} alt="" width="18" />
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content className={styles['pop-in']} align="end">
          <div className={styles['menu']}>
            <DropdownMenu.Label className={styles['menu-title']}>
              Profil
            </DropdownMenu.Label>
            <div className={styles['menu-email']}>{currentUser?.email}</div>
            <DropdownMenu.Item className={styles['close-item']}>
              <button className={styles['close-button']}>
                <SvgIcon
                  src={fullCloseIcon}
                  alt=""
                  width="24"
                  className={styles['close-button-icon']}
                />
              </button>
            </DropdownMenu.Item>
            <DropdownMenu.Item className={styles['menu-item']} asChild>
              <ButtonLink icon={fullProfilIcon} link={{ to: '/profil' }}>
                Voir mon profil
              </ButtonLink>
            </DropdownMenu.Item>
            <DropdownMenu.Separator
              className={cn(styles['separator'], styles['tablet-only'])}
            />
            <DropdownMenu.Label
              className={cn(styles['menu-title'], styles['tablet-only'])}
            >
              Centre d’aide
            </DropdownMenu.Label>
            <div className={styles['tablet-only']}>
              <HelpDropdownMenu />
            </div>
            <DropdownMenu.Separator className={styles['separator']} />
            <DropdownMenu.Item className={styles['menu-item']} asChild>
              <ButtonLink
                icon={fullLogoutIcon}
                link={{ to: `${location.pathname}?logout}` }}
                onClick={() =>
                  logEvent(Events.CLICKED_LOGOUT, {
                    from: location.pathname,
                  })
                }
              >
                Se déconnecter
              </ButtonLink>
            </DropdownMenu.Item>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
