import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullCloseIcon from '@/icons/full-close.svg'
import fullLogoutIcon from '@/icons/full-logout.svg'
import fullProfilIcon from '@/icons/full-profil.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HeaderDropdown.module.scss'

export const HeaderDropdown = () => {
  const { logEvent } = useAnalytics()
  const currentUser = useAppSelector(selectCurrentUser)
  const { pathname } = useLocation()
  const IN_STRUCTURE_CREATION_FUNNEL = pathname.startsWith(
    '/inscription/structure'
  )

  const logEventAndLogout = async () => {
    logEvent(Events.CLICKED_LOGOUT, {
      from: pathname,
    })

    await logout()
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className={styles['dropdown-button']}
          data-testid="profile-button"
          type="button"
        >
          <SvgIcon src={fullProfilIcon} alt="Profil" width="18" />
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={styles['pop-in']}
          align="end"
          sideOffset={7}
        >
          <div
            className={styles['menu']}
            data-testid="header-dropdown-menu-div"
          >
            <DropdownMenu.Item className={styles['close-item']}>
              <button
                type="button"
                aria-label="fermer"
                className={styles['close-button']}
              >
                <SvgIcon src={fullCloseIcon} alt="" width="24" />
              </button>
            </DropdownMenu.Item>
            <DropdownMenu.Label className={styles['menu-title']}>
              Profil
            </DropdownMenu.Label>
            <div className={styles['menu-email']}>{currentUser?.email}</div>
            {!IN_STRUCTURE_CREATION_FUNNEL && (
              <DropdownMenu.Item className={styles['menu-item']}>
                <Button
                  as="a"
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullProfilIcon}
                  to="/profil"
                  label="Voir mon profil"
                />
              </DropdownMenu.Item>
            )}
            <DropdownMenu.Separator className={styles['separator']} />
            <DropdownMenu.Item className={styles['menu-item']}>
              <Button
                icon={fullLogoutIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                onClick={logEventAndLogout}
                label="Se déconnecter"
              />
            </DropdownMenu.Item>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
