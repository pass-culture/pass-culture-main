import cn from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import { useMediaQuery } from 'commons/hooks/useMediaQuery'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { BackToNavLink } from 'components/BackToNavLink/BackToNavLink'
import { Footer } from 'components/Footer/Footer'
import { Header } from 'components/Header/Header'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import { UserReview } from 'components/UserReview/UserReview'
import fullInfoIcon from 'icons/full-info.svg'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { LateralPanel } from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

export interface LayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading?: string
  layout?: 'basic' | 'funnel' | 'onboarding' | 'sticky-actions' | 'logged-out'
  showFooter?: boolean
}

export const Layout = ({
  children,
  mainHeading,
  layout = 'basic',
  showFooter = layout !== 'funnel',
}: LayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const isMobileScreen = useMediaQuery('(max-width: 46.5rem)')

  const shouldDisplayUserReview =
    layout !== 'funnel' && layout !== 'onboarding' && layout !== 'logged-out'

  const mainHeaing = mainHeading && (
    <div className={styles['main-heading-wrapper']}>
      <h1 className={styles['main-heading-title']}>{mainHeading}</h1>
      <BackToNavLink
        isMobileScreen={isMobileScreen}
        className={styles['main-heading-back-to-nav-link']}
      />
    </div>
  )

  return (
    <>
      <div
        className={styles['layout']}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && lateralPanelOpen) {
            setLateralPanelOpen(false)
          }
        }}
      >
        <SkipLinks />
        {currentUser?.isImpersonated && (
          <aside className={styles['connect-as']}>
            <SvgIcon
              src={fullInfoIcon}
              alt="Information"
              width="20"
              className={styles['connect-as-icon']}
            />
            <div className={styles['connect-as-text']}>
              Vous êtes connecté en tant que :&nbsp;
              <strong>
                {currentUser.firstName} {currentUser.lastName}
              </strong>
            </div>
          </aside>
        )}
        {(layout === 'basic' || layout === 'sticky-actions') && (
          <Header
            lateralPanelOpen={lateralPanelOpen}
            setLateralPanelOpen={setLateralPanelOpen}
            focusCloseButton={() => {
              setTimeout(() => {
                closeButtonRef.current?.focus()
              })
            }}
            ref={openButtonRef}
          />
        )}
        <div
          className={cn(styles['page-layout'], {
            [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
            [styles['page-layout-funnel']]: layout === 'funnel',
            [styles['page-layout-onboarding']]: layout === 'onboarding',
          })}
        >
          {(layout === 'basic' || layout === 'sticky-actions') && (
            <LateralPanel
              lateralPanelOpen={lateralPanelOpen}
              setLateralPanelOpen={setLateralPanelOpen}
              openButtonRef={openButtonRef}
              closeButtonRef={closeButtonRef}
              navPanel={navPanel}
            />
          )}
          <div
            id="content-wrapper"
            className={cn(styles['content-wrapper'], {
              [styles['content-wrapper-side']]: layout === 'logged-out',
            })}
          >
            {shouldDisplayUserReview && <UserReview />}
            {layout === 'logged-out' && (
              <header className={styles['content-wrapper-side-logo']}>
                <SvgIcon
                  className={styles['logo-unlogged']}
                  viewBox="0 0 282 120"
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProFullIcon}
                  width="135"
                />
              </header>
            )}
            <div
              className={cn(styles['content-container'], {
                [styles['content-container-funnel']]: layout === 'funnel',
                [styles['content-container-onboarding']]:
                  layout === 'onboarding',
                [styles['content-container-logged-out']]:
                  layout === 'logged-out',
              })}
            >
              <main id="content">
                {layout === 'funnel' || layout === 'onboarding' ? (
                  <>
                    {mainHeaing}
                    {children}
                  </>
                ) : (
                  <div
                    className={cn(styles.content, {
                      [styles['content-logged-out']]: layout === 'logged-out',
                      [styles['content-logged-out-with-heading']]:
                        layout === 'logged-out' && mainHeading,
                    })}
                  >
                    {mainHeaing}
                    {children}
                  </div>
                )}
              </main>
              {showFooter && <Footer layout={layout} />}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
