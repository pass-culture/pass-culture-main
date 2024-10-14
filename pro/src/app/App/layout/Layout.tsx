import cn from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import { Footer } from 'components/Footer/Footer'
import { Header } from 'components/Header/Header'
import { NewNavReview } from 'components/NewNavReview/NewNavReview'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import fullGoTop from 'icons/full-go-top.svg'
import fullInfoIcon from 'icons/full-info.svg'
import { selectCurrentUser } from 'store/user/selectors'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { LateralPanel } from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

export interface LayoutMainHeading {
  text: string
  className?: string
}

export interface LayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading?: LayoutMainHeading
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const Layout = ({
  children,
  mainHeading,
  layout = 'basic',
}: LayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const shouldDisplayNewNavReview =
    Boolean(currentUser?.navState?.eligibilityDate) &&
    layout !== 'funnel' &&
    layout !== 'without-nav'

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
          <div id="content-wrapper" className={styles['content-wrapper']}>
            {shouldDisplayNewNavReview && <NewNavReview />}
            <div
              className={cn(styles['content-container'], {
                [styles['content-container-funnel']]: layout === 'funnel',
              })}
            >
              <main id="content">
                {mainHeading && (
                  <div className={styles['main-heading-wrapper']}>
                    <h1
                      className={cn(
                        styles['main-heading'],
                        mainHeading.className
                      )}
                    >
                      {mainHeading.text}
                    </h1>
                    <a
                      id="back-to-nav-link"
                      href="#lateral-panel"
                      className={styles['back-to-nav-link']}
                    >
                      <SvgIcon
                        src={fullGoTop}
                        alt="Revenir à la barre de navigation"
                        width="20"
                      />
                    </a>
                  </div>
                )}
                {layout === 'funnel' || layout === 'without-nav' ? (
                  children
                ) : (
                  <div className={styles.content}>{children}</div>
                )}
              </main>
              {layout !== 'funnel' && <Footer layout={layout} />}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
