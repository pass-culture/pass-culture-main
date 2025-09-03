/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'
import { useSelector } from 'react-redux'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './FunnelLayout.module.scss'

export interface FunnelLayoutProps {
  children?: React.ReactNode
}

export const FunnelLayout = ({ children }: FunnelLayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    <div className={styles.layout}>
      <SkipLinks shouldDisplayTopPageLink={false} />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}
      <div
        className={cn(styles['page-layout-funnel'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container-funnel']}>
            <main id="content">
              <div id="orejimeElement" />
              {children}
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
