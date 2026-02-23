import { Outlet } from 'react-router'

import { Header } from '@/app/App/layouts/components/Header/Header'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import styles from './WelcomeCarousel.module.scss'

export const WelcomeCarousel = (): JSX.Element => {
  return (
    <div className={styles.layout}>
      <SkipLinks />
      <Header disableHomeLink={true} isUnauthenticated={true} />
      <div className={styles['page-layout']}>
        {/* biome-ignore lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */}
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content" className={styles['content']}>
              <Outlet />
            </main>
          </div>
          <Footer layout={'basic'} />
        </div>
      </div>
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeCarousel
