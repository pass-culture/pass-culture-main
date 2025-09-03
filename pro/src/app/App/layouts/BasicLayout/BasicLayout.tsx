/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'
import { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './BasicLayout.module.scss'
import { LateralPanel } from './LateralPanel/LateralPanel'

interface BasicLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading?: React.ReactNode
  /**
   * Complementary name of the page to display in the main heading,
   * as a subheading.
   */
  mainSubHeading?: string
  /**
   * Any content to display above the main heading.
   */
  mainTopElement?: React.ReactNode
  /**
   * In case both `<h1>` & back to nav link
   * had to be declared within the children
   */
  areMainHeadingAndBackToNavLinkInChild?: boolean
  /**
   * When StickyActionBar is rendered within the children,
   * Footer needs to have a special margin-bottom to be visible
   * above it.
   */
  isStickyActionBarInChild?: boolean
}

export const BasicLayout = ({
  children,
  mainHeading,
  mainSubHeading,
  mainTopElement,
  areMainHeadingAndBackToNavLinkInChild = false,
  isStickyActionBarInChild = false,
}: BasicLayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const isConnected = !!currentUser
  const isBackToNavLinkDisplayed =
    areMainHeadingAndBackToNavLinkInChild || (mainHeading && isConnected)

  const mainHeadingWrapper = mainHeading ? (
    <MainHeading
      mainHeading={mainHeading}
      mainSubHeading={mainSubHeading}
      isConnected={isConnected}
    />
  ) : null

  return (
    <div className={styles.layout}>
      <SkipLinks shouldDisplayTopPageLink={!isBackToNavLinkDisplayed} />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}
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
      <div
        className={cn(styles['page-layout-main'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <LateralPanel
          lateralPanelOpen={lateralPanelOpen}
          setLateralPanelOpen={setLateralPanelOpen}
          openButtonRef={openButtonRef}
          closeButtonRef={closeButtonRef}
          navPanel={navPanel}
        />
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content">
              <div id="orejimeElement" />
              {mainTopElement}
              <div className={styles.content}>
                {mainHeadingWrapper}
                {children}
              </div>
            </main>
            <Footer
              layout={isStickyActionBarInChild ? 'sticky-basic' : 'basic'}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
