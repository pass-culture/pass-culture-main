/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import { type ReactNode, useRef, useState } from 'react'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './BasicLayout.module.scss'
import { LateralPanel } from './LateralPanel/LateralPanel'

interface BasicLayoutProps {
  children?: ReactNode
  /**
   * When StickyActionBar is rendered within the children,
   * Footer needs to have a special margin-bottom to be visible
   * above it.
   */
  isStickyActionBarInChild?: boolean
  /**
   * Optional: configure the back button in the header
   */
  isAdminArea?: boolean
}

export const BasicLayout = ({
  children,
  isStickyActionBarInChild = false,
  isAdminArea = false,
}: BasicLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)
  const [isLateralPanelOpen, setIsLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  return (
    <div className={styles.layout}>
      <SkipLinks />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}
      <Header
        isLateralPanelOpen={isLateralPanelOpen}
        onToggleLateralPanel={setIsLateralPanelOpen}
        focusCloseButton={() => {
          setTimeout(() => {
            closeButtonRef.current?.focus()
          })
        }}
        ref={openButtonRef}
        isAdminArea={isAdminArea}
      />

      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        {/* TODO (igabriele, 2026-04-29): Move lateral panels into `<AdministrationLayout>` and `<PartnerLayout>`. */}
        <LateralPanel
          isOpen={isLateralPanelOpen}
          onToggle={setIsLateralPanelOpen}
          openButtonRef={openButtonRef}
          closeButtonRef={closeButtonRef}
          navPanel={navPanel}
          isAdminArea={isAdminArea}
        />
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content" tabIndex={-1}>
              <div className={styles.content}>{children}</div>
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
