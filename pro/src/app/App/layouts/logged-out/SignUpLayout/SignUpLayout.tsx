/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type React from 'react'
import { NavLink } from 'react-router'

import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'
import logoPassCultureProFullIcon from '@/icons/logo-pass-culture-pro-full.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { BubbleSVG } from './assets/BubbleSVG'
import { CitationSVG } from './assets/CitationSVG'
import macStudioImage from './assets/mac-studio.png'
import styles from './SignUpLayout.module.scss'

interface SignUpLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
}

export const SignUpLayout = ({ children, mainHeading }: SignUpLayoutProps) => {
  return (
    <div className={styles.layout}>
      <SkipLinks />
      <div className={styles['page-layout']}>
        <div
          id="content-wrapper"
          className={cn(
            styles['content-wrapper'],
            styles['content-wrapper-right-side']
          )}
        >
          <header
            className={styles['content-wrapper-right-side-logo']}
            data-testid="sign-up-header"
          >
            <div className={styles['image-engagements']}>
              <p className={styles['image-engagements-text-1']}>
                + de 4 millions de jeunes scolarisés ont participé à{' '}
                <span className={styles['image-engagements-text-emphasis']}>
                  une sortie scolaire
                </span>
                <span className={styles['citation-icon-1']}>
                  <CitationSVG />
                </span>
              </p>
              <p className={styles['image-engagements-text-2']}>
                + de{' '}
                <span className={styles['image-engagements-text-emphasis']}>
                  36 000 acteurs culturels
                </span>{' '}
                déjà inscrits
                <span className={styles['citation-icon-2']}>
                  <CitationSVG />
                </span>
              </p>
              <p className={styles['image-engagements-text-3']}>
                + de 2 millions de jeunes ont{' '}
                <span className={styles['image-engagements-text-emphasis']}>
                  déjà réservé une offre
                </span>{' '}
                via l’application
                <span className={styles['citation-icon-3']}>
                  <CitationSVG />
                </span>
              </p>
            </div>
            <div className={styles['image-laptop']}>
              <BubbleSVG />
              <img
                src={macStudioImage}
                alt=""
                className={styles['image-laptop-macstudio']}
              />
            </div>
          </header>
          <div className={styles['content-container']}>
            <NavLink className={styles['logo-sign-up']} to="/connexion">
              <SvgIcon
                viewBox="0 0 282 120"
                alt="Pass Culture pro, l’espace des acteurs culturels"
                src={logoPassCultureProFullIcon}
                width="135"
                data-testid="sign-up-logo"
              />
            </NavLink>
            <main id="content">
              <div className={cn(styles.content, styles[`content-sign-up`])}>
                <MainHeading mainHeading={mainHeading} />
                {children}
              </div>
            </main>
            <Footer layout="sign-up" />
          </div>
        </div>
      </div>
    </div>
  )
}
