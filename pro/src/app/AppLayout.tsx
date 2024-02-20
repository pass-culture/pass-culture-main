import classnames from 'classnames'
import React, { useRef, useState } from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import SkipLinks from 'components/SkipLinks'
import useActiveFeature from 'hooks/useActiveFeature'
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
  layout?: 'basic' | 'funnel' | 'without-nav'
}

export const AppLayout = ({
  children,
  className,
  pageName = 'Accueil',
  layout = 'basic',
}: AppLayoutProps) => {
  const isNewSideBarNavigation = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  return (
    <>
      <div
        id="lateral-panel"
        className={classnames({
          'lateral-panel-wrapper': true,
          open: lateralPanelOpen,
        })}
      >
        <div className={'lateral-panel-menu'}>
          <div
            className={classnames({
              'lateral-panel-nav': true,
              'lateral-panel-nav-open': lateralPanelOpen,
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
        </div>
      </div>
      <SkipLinks />
      {layout == 'basic' && (
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
      <main
        id="content"
        className={classnames(
          {
            page: true,
            [`${pageName}-page`]: true,
            'page-content': isNewSideBarNavigation,
            container: layout === 'basic',

            'without-nav': layout === 'without-nav',
          },
          className
        )}
      >
        {layout === 'funnel' || layout === 'without-nav' ? (
          children
        ) : (
          <div className="page-content">
            <div className={classnames('after-notification-content')}>
              <DomainNameBanner />
              {children}
            </div>
          </div>
        )}
      </main>
    </>
  )
}
