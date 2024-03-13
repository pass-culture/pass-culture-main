import classnames from 'classnames'
import React, { useRef, useState } from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Footer from 'components/Footer/Footer'
import Header from 'components/Header/Header'
import SideNavLinks from 'components/SideNavLinks/SideNavLinks'
import SkipLinks from 'components/SkipLinks'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AppLayout.module.scss'

export interface AppLayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const AppLayout = ({
  children,
  className,
  pageName = 'Accueil',
  layout = 'basic',
}: AppLayoutProps) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  return (
    <>
      <SkipLinks />
      {(layout === 'basic' || layout === 'sticky-actions') && (
        <Header
          lateralPanelOpen={lateralPanelOpen}
          isTopMenuVisible={layout === 'basic' || layout === 'sticky-actions'}
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
        className={classnames({
          [styles['page-layout']]: true,
          [styles['page-layout-full']]: layout === 'without-nav',
          [styles[`content-layout-${layout}`]]: isNewSideBarNavigation,
        })}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && lateralPanelOpen) {
            setLateralPanelOpen(false)
          }
        }}
      >
        {isNewSideBarNavigation && layout == 'basic' && (
          <nav
            id="lateral-panel"
            className={classnames({
              [styles['lateral-panel-wrapper']]: true,
              [styles['lateral-panel-wrapper-open']]: lateralPanelOpen,
            })}
            ref={navPanel}
            aria-label="Menu principal"
          >
            <div className={styles['lateral-panel-menu']}>
              {lateralPanelOpen && (
                <div
                  className={classnames({
                    [styles['lateral-panel-nav']]: true,
                    [styles['lateral-panel-nav-open']]: lateralPanelOpen,
                  })}
                >
                  <Button
                    aria-expanded={lateralPanelOpen}
                    variant={ButtonVariant.TERNARY}
                    onClick={() => {
                      setLateralPanelOpen(!lateralPanelOpen)
                      openButtonRef.current?.focus()
                    }}
                    aria-label="Fermer"
                    aria-controls="lateral-panel"
                    ref={closeButtonRef}
                    className={styles['lateral-panel-nav-button']}
                  >
                    <SvgIcon src={strokeCloseIcon} alt="" width="24" />
                  </Button>
                  <SvgIcon
                    alt="Pass Culture pro, l’espace des acteurs culturels"
                    src={logoPassCultureProIcon}
                    viewBox="0 0 119 40"
                    width="119"
                    className="logo"
                  />
                </div>
              )}
              <SideNavLinks isLateralPanelOpen={lateralPanelOpen} />
            </div>
          </nav>
        )}
        <div className={styles['main-wrapper']}>
          <main
            id="content"
            className={classnames(
              {
                page: true,
                [`${pageName}-page`]: true,
                [styles['container-full']]:
                  isNewSideBarNavigation && layout === 'basic',
                [styles.container]:
                  layout === 'basic' || layout === 'sticky-actions',
                [styles['container-without-nav']]: layout === 'without-nav',
                [styles[`content-layout-${layout}`]]: isNewSideBarNavigation,
              },
              className
            )}
          >
            {layout === 'funnel' || layout === 'without-nav' ? (
              children
            ) : (
              <div
                className={classnames({
                  [styles['page-content']]: true,
                  [styles['page-content-old']]: !isNewSideBarNavigation,
                })}
              >
                <div className={styles['after-notification-content']}>
                  <DomainNameBanner />
                  {children}
                </div>
              </div>
            )}
          </main>
          <Footer layout={layout} />
        </div>
      </div>
    </>
  )
}
