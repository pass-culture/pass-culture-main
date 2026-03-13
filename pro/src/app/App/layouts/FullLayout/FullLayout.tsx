/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */

import cn from 'classnames'
import type React from 'react'

import { ConnectedAsAside } from '@/app/App/layouts/components/ConnectedAsAside/ConnectedAsAside'
import { Header } from '@/app/App/layouts/components/Header/Header'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './FullLayout.module.scss'

interface FullLayoutProps {
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
}

export const FullLayout = ({
  children,
  mainHeading,
  mainSubHeading,
}: FullLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)

  return (
    <div className={styles.layout}>
      <SkipLinks />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}

      <Header />

      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content" tabIndex={-1}>
              <div className={styles['content']}>
                <MainHeading
                  mainHeading={mainHeading}
                  mainSubHeading={mainSubHeading}
                />

                {children}
              </div>
            </main>
            <Footer layout={'basic'} />
          </div>
        </div>
      </div>
    </div>
  )
}
