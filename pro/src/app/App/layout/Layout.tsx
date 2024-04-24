import classnames from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import DomainNameBanner from 'components/DomainNameBanner'
import Footer from 'components/Footer/Footer'
import Header from 'components/Header/Header'
import NewNavReview from 'components/NewNavReview/NewNavReview'
import SkipLinks from 'components/SkipLinks'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import { selectCurrentUser } from 'store/user/selectors'

import LateralPanel from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

interface LayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const Layout = ({
  children,
  className,
  pageName = 'Accueil',
  layout = 'basic',
}: LayoutProps) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const shouldDisplayNewNavReview =
    isNewSideBarNavigation &&
    Boolean(currentUser?.navState?.eligibilityDate) &&
    layout !== 'funnel' &&
    layout !== 'without-nav'

  return (
    <>
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
        className={classnames({
          [styles['page-layout']]: true,
          [styles['page-layout-full']]: layout === 'without-nav',
          [styles[`content-layout-${layout}`]]: isNewSideBarNavigation,
          [styles[`content-layout-${layout}-with-review-banner`]]:
            shouldDisplayNewNavReview,
        })}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && lateralPanelOpen) {
            setLateralPanelOpen(false)
          }
        }}
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
          className={classnames({
            [styles['main-wrapper']]: true,
            [styles['main-wrapper-old']]:
              !isNewSideBarNavigation || layout === 'funnel',
          })}
        >
          {shouldDisplayNewNavReview && <NewNavReview />}
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
                [styles['container-sticky-actions']]:
                  layout === 'sticky-actions',
                [styles['container-sticky-actions-new-interface']]:
                  isNewSideBarNavigation && layout === 'sticky-actions',
                [styles['container-without-nav']]: layout === 'without-nav',
                [styles[`content-layout`]]: isNewSideBarNavigation,
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
                  [styles['page-content-with-review-banner']]:
                    isNewSideBarNavigation &&
                    Boolean(currentUser?.navState?.eligibilityDate),
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
          {layout !== 'funnel' && <Footer layout={layout} />}
        </div>
      </div>
    </>
  )
}
