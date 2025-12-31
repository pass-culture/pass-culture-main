import cn from 'classnames'
import type React from 'react'
import { useRef, useState } from 'react'

import { LateralPanel } from '@/app/App/layouts/BasicLayout/LateralPanel/LateralPanel'
import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './FunnelLayout.module.scss'

export interface FunnelLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
  withFlexContent?: boolean
  tabIndex?: number
}

export const FunnelLayout = ({
  children,
  mainHeading,
  withFlexContent = false,
  tabIndex,
}: FunnelLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)
  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)
  const isMobile = useMediaQuery('(max-width: 64rem)')

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
        disableHomeLink={!currentUser?.hasUserOfferer}
      />
      {isMobile && (
        <LateralPanel
          lateralPanelOpen={lateralPanelOpen}
          setLateralPanelOpen={setLateralPanelOpen}
          openButtonRef={openButtonRef}
          closeButtonRef={closeButtonRef}
          navPanel={navPanel}
        />
      )}
      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        {/* biome-ignore lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */}
        <div
          id="content-wrapper"
          className={cn(styles['content-wrapper'], {
            [styles['content-wrapper-flex']]: withFlexContent,
          })}
        >
          <div className={styles['content-container']}>
            <main
              id="content"
              className={
                withFlexContent ? styles['content-flex'] : styles['content']
              }
              // TODO: tabIndex={-1} breaks the ability to click on a multiselect element label.
              tabIndex={tabIndex}
            >
              <MainHeading mainHeading={mainHeading} />

              {children}
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
