/** biome-ignore-all lint/correctness/useUniqueElementIds: Header is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import { type ForwardedRef, forwardRef } from 'react'
import { NavLink, useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import fullBurgerIcon from '@/icons/full-burger.svg'
import logoPassCultureProIcon from '@/icons/logo-pass-culture-pro.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { HeaderDropdown } from './components/HeaderDropdown/HeaderDropdown'
import { HeaderHelpDropdown } from './components/HeaderHelpDropdown/HeaderHelpDropdown'
import { UserReviewDialog } from './components/UserReviewDialog/UserReviewDialog'
import styles from './Header.module.scss'

type HeaderProps = {
  isLateralPanelOpen?: boolean
  onToggleLateralPanel?: (state: boolean) => void
  focusCloseButton?: () => void
  disableHomeLink?: boolean
  isAdminArea?: boolean
}

export const Header = forwardRef(
  (
    {
      isLateralPanelOpen = false,
      onToggleLateralPanel,
      focusCloseButton,
      disableHomeLink = false,
      isAdminArea = false,
    }: HeaderProps,
    openButtonRef: ForwardedRef<HTMLButtonElement>
  ) => {
    const isProFeedbackEnabled = useActiveFeature('ENABLE_PRO_FEEDBACK')
    const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

    const { logEvent } = useAnalytics()
    const location = useLocation()

    return (
      <header className={styles['top-menu']}>
        <div className={styles['top-menu-content']}>
          {!disableHomeLink && (
            <div className={styles['burger-icon']}>
              <Button
                id="header-nav-toggle"
                ref={openButtonRef}
                aria-expanded={isLateralPanelOpen}
                color={ButtonColor.NEUTRAL}
                aria-controls="lateral-panel"
                onClick={() => {
                  onToggleLateralPanel?.(!isLateralPanelOpen)
                  focusCloseButton?.()
                }}
                variant={ButtonVariant.TERTIARY}
                icon={fullBurgerIcon}
                iconAlt="Menu"
              />
            </div>
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
            {!withSwitchVenueFeature && (
              <div className={styles['top-right-menu-links']}>
                <div className={styles['tablet-and-above']}>
                  {isProFeedbackEnabled && <UserReviewDialog />}
                </div>
                <div className={styles['tablet-and-above']}>
                  <HeaderHelpDropdown />
                </div>
              </div>
            )}
            {withSwitchVenueFeature && (
              <div
                className={cn(
                  styles['tablet-and-above'],
                  styles['is-switch-venue']
                )}
              >
                <Button
                  as="a"
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.BRAND}
                  size={ButtonSize.SMALL}
                  to={isAdminArea ? '/accueil' : '/remboursements'}
                  iconPosition={IconPositionEnum.LEFT}
                  icon={isAdminArea ? fullBackIcon : strokeRepaymentIcon}
                  label={
                    isAdminArea
                      ? 'Revenir à l’Espace Partenaire'
                      : 'Espace administration'
                  }
                />
              </div>
            )}
            <HeaderDropdown />
          </div>
        </div>
      </header>
    )
  }
)
Header.displayName = 'Header'
