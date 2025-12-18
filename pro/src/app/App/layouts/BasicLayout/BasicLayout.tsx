/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'
import { useRef, useState } from 'react'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
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
  mainHeading: React.ReactNode
  /**
   * Complementary name of the page to display in the main heading,
   * as a subheading.
   */
  mainSubHeading?: string
  /**
   * When StickyActionBar is rendered within the children,
   * Footer needs to have a special margin-bottom to be visible
   * above it.
   */
  isStickyActionBarInChild?: boolean
  /**
   * Optional: configure the back button in the header
   */
  backTo?: { to: string }
}

export const BasicLayout = ({
  children,
  mainHeading,
  mainSubHeading,
  isStickyActionBarInChild = false,
  backTo = { to: '/administration' },
}: BasicLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const mainHeadingWrapper = (
    <MainHeading
      className={styles['main-heading']}
      mainHeading={mainHeading}
      mainSubHeading={mainSubHeading}
      shouldDisplayBackToNavLink
    />
  )

  return (
    <div className={styles.layout}>
      <SkipLinks />
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
        backTo={backTo}
      />
      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <LateralPanel
          lateralPanelOpen={lateralPanelOpen}
          setLateralPanelOpen={setLateralPanelOpen}
          openButtonRef={openButtonRef}
          closeButtonRef={closeButtonRef}
          navPanel={navPanel}
          isAdminPanel={backTo.to === '/accueil'}
        />
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content">
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
