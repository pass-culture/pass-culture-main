/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
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
}

export const FunnelLayout = ({ children, mainHeading }: FunnelLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)

  return (
    <div className={styles.layout}>
      <SkipLinks />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}
      <Header disableHomeLink={!currentUser?.hasUserOfferer} />
      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content">
              <div className={styles.content}>
                <MainHeading mainHeading={mainHeading} />
                {children}
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
