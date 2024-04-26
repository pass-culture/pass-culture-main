import cn from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import { DomainNameBanner } from 'components/DomainNameBanner/DomainNameBanner'
import Footer from 'components/Footer/Footer'
import Header from 'components/Header/Header'
import NewNavReview from 'components/NewNavReview/NewNavReview'
import SkipLinks from 'components/SkipLinks'
import { selectCurrentUser } from 'store/user/selectors'

import LateralPanel from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

interface LayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const Layout = ({ children, layout = 'basic' }: LayoutProps) => {
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
          <div
            className={cn(styles['content-container'], {
              [styles['content-container-funnel']]: layout === 'funnel',
            })}
          >
            <div>
              {shouldDisplayNewNavReview && <NewNavReview />}
              <main id="content">
                {layout === 'funnel' || layout === 'without-nav' ? (
                  children
                ) : (
                  <div className={styles.content}>
                    <DomainNameBanner />
                    {children}
                  </div>
                )}
              </main>
            </div>
            {layout !== 'funnel' && <Footer layout={layout} />}
          </div>
        </div>
      </div>
    </>
  )
}
