/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'
import { useRef, useState } from 'react'

import { Header } from '@/app/App/layouts/components/Header/Header'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import { ConnectedAsAside } from '../components/ConnectedAsAside/ConnectedAsAside'
import { Footer } from '../components/Footer/Footer'
import styles from './ContentLayout.module.scss'
import { LateralPanel } from './LateralPanel/LateralPanel'

type ContentLayoutProps = {
  children: React.ReactNode
  isAdminArea?: boolean
}

export const ContentLayout = ({
  children,
  isAdminArea = false,
}: Readonly<ContentLayoutProps>): JSX.Element => {
  const currentUser = useAppSelector(selectCurrentUser)
  const [isLateralPanelOpen, setIsLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const userIsConnectedAs = currentUser?.isImpersonated

  return (
    <div className={styles.layout}>
      <SkipLinks />
      {userIsConnectedAs && <ConnectedAsAside currentUser={currentUser} />}
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
          [styles['page-layout-connect-as']]: userIsConnectedAs,
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
          <main id="content" className={styles.content} tabIndex={-1}>
            {children}
          </main>
          <Footer />
        </div>
      </div>
    </div>
  )
}
