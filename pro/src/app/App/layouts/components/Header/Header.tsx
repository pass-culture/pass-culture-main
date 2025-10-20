/** biome-ignore-all lint/correctness/useUniqueElementIds: Header is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import { type ForwardedRef, forwardRef } from 'react'
import { NavLink, useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import fullBurgerIcon from '@/icons/full-burger.svg'
import logoPassCultureProIcon from '@/icons/logo-pass-culture-pro.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { HeaderDropdown } from './components/HeaderDropdown/HeaderDropdown'
import { HeaderHelpDropdown } from './components/HeaderHelpDropdown/HeaderHelpDropdown'
import { HeaderVenuesDropdown } from './components/HeaderVenuesDropdown/HeaderVenuesDropdown'
import { UserReviewDialog } from './components/UserReviewDialog/UserReviewDialog'
import styles from './Header.module.scss'

type HeaderProps = {
  lateralPanelOpen?: boolean
  setLateralPanelOpen?: (state: boolean) => void
  focusCloseButton?: () => void
  disableHomeLink?: boolean
}

export const Header = forwardRef(
  (
    {
      lateralPanelOpen = false,
      setLateralPanelOpen = () => undefined,
      focusCloseButton = () => undefined,
      disableHomeLink = false,
    }: HeaderProps,
    openButtonRef: ForwardedRef<HTMLButtonElement>
  ) => {
    const { logEvent } = useAnalytics()
    const location = useLocation()
    const selectedVenue = useAppSelector((state) => state.user.selectedVenue)
    const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
    const isProFeedbackEnabled = useActiveFeature('ENABLE_PRO_FEEDBACK')

    return (
      <header className={styles['top-menu']}>
        <div className={styles['top-menu-content']}>
          {!disableHomeLink && (
            <Button
              id="header-nav-toggle"
              ref={openButtonRef}
              aria-expanded={lateralPanelOpen}
              className={styles['burger-icon']}
              variant={ButtonVariant.TERNARY}
              onClick={() => {
                setLateralPanelOpen(!lateralPanelOpen)
                focusCloseButton()
              }}
              aria-controls="lateral-panel"
            >
              <SvgIcon src={fullBurgerIcon} alt="Menu" width="24" />
            </Button>
          )}
          <div className={styles['nav-brand']}>
            {disableHomeLink ? (
              <div className={cn(styles.logo, styles['logo-link-disabled'])}>
                <SvgIcon
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProIcon}
                  viewBox="0 0 119 40"
                  width="119"
                />
              </div>
            ) : (
              <NavLink
                className={styles.logo}
                to="/accueil"
                onClick={() => {
                  logEvent(Events.CLICKED_PRO, { from: location.pathname })
                }}
              >
                <SvgIcon
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProIcon}
                  viewBox="0 0 119 40"
                  width="119"
                />
              </NavLink>
            )}
          </div>
          <div className={styles['top-right-menu']}>
            <div className={styles['top-right-menu-links']}>
              <div className={styles['tablet-and-above']}>
                {isProFeedbackEnabled && <UserReviewDialog />}
              </div>
              {withSwitchVenueFeature && selectedVenue && (
                <div className={styles['tablet-and-above']}>
                  <HeaderVenuesDropdown />
                </div>
              )}
              <div className={styles['tablet-and-above']}>
                <HeaderHelpDropdown />
              </div>
            </div>
            <HeaderDropdown />
          </div>
        </div>
      </header>
    )
  }
)
Header.displayName = 'Header'
