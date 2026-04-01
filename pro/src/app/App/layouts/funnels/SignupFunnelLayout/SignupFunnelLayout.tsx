import type React from 'react'

import { Header } from '@/app/App/layouts/components/Header/Header'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './SignupFunnelLayout.module.scss'

export const SignupFunnelLayout = ({
  children,
}: Readonly<{ children?: React.ReactNode }>): JSX.Element => {
  return (
    <div className={styles.layout}>
      <SkipLinks />
      <Header disableHomeLink isUnauthenticated />
      <div className={styles['page-layout']}>
        {/* biome-ignore lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */}
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content" className={styles['content']} tabIndex={-1}>
              {children}
            </main>
          </div>
          <Footer layout={'basic'} />
        </div>
      </div>
    </div>
  )
}
