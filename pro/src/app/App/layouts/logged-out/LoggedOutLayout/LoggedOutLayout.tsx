/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'

import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'
import logoPassCultureProFullIcon from '@/icons/logo-pass-culture-pro-full.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './LoggedOutLayout.module.scss'

interface LoggedOutLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
}

export const LoggedOutLayout = ({
  children,
  mainHeading,
}: LoggedOutLayoutProps) => {
  return (
    <div className={styles.layout}>
      <SkipLinks />
      <div className={styles['page-layout']}>
        <div
          id="content-wrapper"
          className={cn(
            styles['content-wrapper'],
            styles['content-wrapper-left-side']
          )}
        >
          <header className={styles['content-wrapper-left-side-logo']}>
            <SvgIcon
              className={styles['logo-unlogged']}
              viewBox="0 0 282 120"
              alt="Pass Culture pro, l’espace des acteurs culturels"
              src={logoPassCultureProFullIcon}
              width="135"
            />
          </header>
          <div className={styles['content-container']}>
            <main id="content">
              <div className={cn(styles.content, styles[`content-logged-out`])}>
                <MainHeading mainHeading={mainHeading} />
                {children}
              </div>
            </main>
            <Footer layout="logged-out" />
          </div>
        </div>
      </div>
    </div>
  )
}
