/** biome-ignore-all lint/correctness/useUniqueElementIds: Header is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import { type ForwardedRef, forwardRef } from 'react'
import { NavLink, useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  TABLET_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  type ButtonProps,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import fullBurgerIcon from '@/icons/full-burger.svg'
import fullSmsIcon from '@/icons/full-sms.svg'
import logoPassCultureProIcon from '@/icons/logo-pass-culture-pro.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { UserReviewDialog } from '../../BasicLayout/LateralPanel/SideNavLinks/components/UserReviewDialog/UserReviewDialog'
import { HeaderDropdown } from './components/HeaderDropdown/HeaderDropdown'
import { HeaderHelpDropdown } from './components/HeaderHelpDropdown/HeaderHelpDropdown'
import styles from './Header.module.scss'

interface HeaderProps {
  isLateralPanelOpen?: boolean
  onToggleLateralPanel?: (state: boolean) => void
  focusCloseButton?: () => void
  hideAdminButton?: boolean
  disableBurgerMenu?: boolean
  disableHomeLink?: boolean
  isUnauthenticated?: boolean
  isAdminArea?: boolean
}

export const Header = forwardRef(
  (
    {
      isLateralPanelOpen = false,
      onToggleLateralPanel,
      focusCloseButton,
      hideAdminButton = false,
      disableBurgerMenu = false,
      disableHomeLink = false,
      isUnauthenticated = false,
      isAdminArea = false,
    }: Readonly<HeaderProps>,
    openButtonRef: ForwardedRef<HTMLButtonElement>
  ) => {
    const isProFeedbackEnabled = useActiveFeature('ENABLE_PRO_FEEDBACK')
    const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

    const { logEvent } = useAnalytics()
    const location = useLocation()

    const showBurgerMenu = !disableBurgerMenu && !disableHomeLink

    const isTablet = useMediaQuery(TABLET_MEDIA_QUERY)

    const adminButtonLabel = isAdminArea
      ? 'Revenir à l’Espace Partenaire'
      : 'Espace administration'

    // In mobile mode, we don't use a button label, BUT we must have an aria-label in backup for assistive technologies
    const adminButtonLabelProps: Pick<ButtonProps, 'label' | 'aria-label'> =
      isTablet
        ? {
            'aria-label': adminButtonLabel,
          }
        : {
            label: adminButtonLabel,
          }

    return (
      <header className={styles['top-menu']}>
        <div className={styles['top-menu-content']}>
          {showBurgerMenu && (
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
            {!isUnauthenticated && (
              <>
                {!withSwitchVenueFeature && (
                  <div className={styles['top-right-menu-links']}>
                    <div className={styles['tablet-and-above']}>
                      {isProFeedbackEnabled && (
                        <UserReviewDialog
                          dialogTrigger={
                            <Button
                              color={ButtonColor.NEUTRAL}
                              icon={fullSmsIcon}
                              label="Donner mon avis"
                              size={ButtonSize.SMALL}
                              variant={ButtonVariant.TERTIARY}
                            />
                          }
                        />
                      )}
                    </div>
                    <div className={styles['tablet-and-above']}>
                      <HeaderHelpDropdown />
                    </div>
                  </div>
                )}
                {withSwitchVenueFeature && !hideAdminButton && (
                  <Button
                    as="a"
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.BRAND}
                    size={ButtonSize.SMALL}
                    to={isAdminArea ? '/accueil' : '/remboursements'}
                    iconPosition={IconPositionEnum.LEFT}
                    icon={isAdminArea ? fullBackIcon : strokeRepaymentIcon}
                    onClick={() => {
                      if (!isAdminArea) {
                        logEvent(Events.CLICKED_HEADER_ADMIN_BUTTON, {
                          from: location.pathname,
                        })
                      }
                    }}
                    {...adminButtonLabelProps}
                  />
                )}
                <HeaderDropdown />
              </>
            )}
            {isUnauthenticated && (
              <Button
                as="a"
                to="https://aide.passculture.app/hc/fr"
                opensInNewTab={true}
                isExternal={true}
                color={ButtonColor.NEUTRAL}
                variant={ButtonVariant.SECONDARY}
                label="Besoin d’aide ?"
                size={ButtonSize.SMALL}
              />
            )}
          </div>
        </div>
      </header>
    )
  }
)
Header.displayName = 'Header'
