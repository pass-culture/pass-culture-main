import cn from 'classnames'
import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { NavLink } from 'react-router'

import { selectCurrentUser } from '@/commons/store/user/selectors'
import { BackToNavLink } from '@/components/BackToNavLink/BackToNavLink'
import { Footer } from '@/components/Footer/Footer'
import { Header } from '@/components/Header/Header'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'
import fullInfoIcon from '@/icons/full-info.svg'
import logoPassCultureProFullIcon from '@/icons/logo-pass-culture-pro-full.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { BubbleSVG } from './assets/BubbleSVG'
import { CitationSVG } from './assets/CitationSVG'
import macStudioImage from './assets/mac-studio.png'
import { LateralPanel } from './LateralPanel/LateralPanel'
import styles from './Layout.module.scss'

export interface LayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading?: React.ReactNode
  /**
   * Complementary name of the page to display in the main heading,
   * as a subheading.
   */
  mainSubHeading?: string
  /**
   * Any content to display above the main heading.
   */
  mainTopElement?: React.ReactNode
  /**
   * In case both `<h1>` & back to nav link
   * had to be declared within the children
   */
  areMainHeadingAndBackToNavLinkInChild?: boolean
  layout?:
    | 'basic'
    | 'funnel'
    | 'onboarding'
    | 'sticky-actions'
    | 'sticky-onboarding'
    | 'logged-out'
    | 'sign-up'
  showFooter?: boolean
}

interface MainHeadingProps {
  className?: string
  mainHeading: React.ReactNode
  mainSubHeading?: string
  isConnected?: boolean
}
export const MainHeading = ({
  className,
  mainHeading,
  mainSubHeading,
  isConnected = true,
}: MainHeadingProps): JSX.Element => {
  return (
    <div
      className={cn(className, styles['main-heading-wrapper'], {
        [styles['main-heading-wrapper-with-subtitle']]: mainSubHeading,
      })}
    >
      <h1 className={styles['main-heading-title']}>
        {mainHeading}
        {mainSubHeading && (
          <span className={styles['main-heading-subtitle']}>
            {mainSubHeading}
          </span>
        )}
      </h1>
      {isConnected && (
        <BackToNavLink
          className={cn(styles['main-heading-back-to-nav-link'], {
            [styles['main-heading-back-to-nav-link-with-subtitle']]:
              mainSubHeading,
          })}
        />
      )}
    </div>
  )
}

export const Layout = ({
  children,
  mainHeading,
  mainSubHeading,
  mainTopElement,
  layout = 'basic',
  showFooter = layout !== 'funnel',
  areMainHeadingAndBackToNavLinkInChild = false,
}: LayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const [lateralPanelOpen, setLateralPanelOpen] = useState(false)

  const openButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const navPanel = useRef<HTMLDivElement>(null)

  const isConnected = !!currentUser
  const isBackToNavLinkDisplayed =
    areMainHeadingAndBackToNavLinkInChild || (mainHeading && isConnected)

  const mainHeadingWrapper = mainHeading ? (
    // eslint-disable-next-line react/forbid-elements
    <MainHeading
      mainHeading={mainHeading}
      mainSubHeading={mainSubHeading}
      isConnected={isConnected}
    />
  ) : null

  return (
    <>
      <div
        className={styles['layout']}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && lateralPanelOpen) {
            setLateralPanelOpen(false)
          }
        }}
      >
        <SkipLinks shouldDisplayTopPageLink={!isBackToNavLinkDisplayed} />
        {currentUser?.isImpersonated && (
          <aside className={styles['connect-as']}>
            <SvgIcon
              src={fullInfoIcon}
              alt="Information"
              width="20"
              className={styles['connect-as-icon']}
            />
            <div className={styles['connect-as-text']}>
              Vous êtes connecté en tant que :&nbsp;
              <strong>
                {currentUser.firstName} {currentUser.lastName}
              </strong>
            </div>
          </aside>
        )}
        {(layout === 'basic' ||
          layout === 'sticky-actions' ||
          layout === 'onboarding' ||
          layout === 'sticky-onboarding') && (
          <Header
            lateralPanelOpen={lateralPanelOpen}
            setLateralPanelOpen={setLateralPanelOpen}
            focusCloseButton={() => {
              setTimeout(() => {
                closeButtonRef.current?.focus()
              })
            }}
            ref={openButtonRef}
            disableHomeLink={
              layout === 'sticky-onboarding' || layout === 'onboarding'
            }
          />
        )}
        <div
          className={cn(
            styles['page-layout'],
            styles[`page-layout-${layout}`],
            {
              [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
            }
          )}
        >
          {(layout === 'basic' || layout === 'sticky-actions') && (
            <LateralPanel
              lateralPanelOpen={lateralPanelOpen}
              setLateralPanelOpen={setLateralPanelOpen}
              openButtonRef={openButtonRef}
              closeButtonRef={closeButtonRef}
              navPanel={navPanel}
            />
          )}
          <div
            id="content-wrapper"
            className={cn(styles['content-wrapper'], {
              [styles['content-wrapper-left-side']]: layout === 'logged-out',
              [styles['content-wrapper-right-side']]: layout === 'sign-up',
            })}
          >
            {layout === 'logged-out' && (
              <header className={styles['content-wrapper-left-side-logo']}>
                <SvgIcon
                  className={styles['logo-unlogged']}
                  viewBox="0 0 282 120"
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProFullIcon}
                  width="135"
                />
              </header>
            )}
            {layout === 'sign-up' && (
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
            )}
            <div
              className={cn(
                styles['content-container'],
                styles[`content-container-${layout}`]
              )}
            >
              {layout === 'sign-up' && (
                <NavLink className={styles['logo-sign-up']} to="/connexion">
                  <SvgIcon
                    viewBox="0 0 282 120"
                    alt="Pass Culture pro, l’espace des acteurs culturels"
                    src={logoPassCultureProFullIcon}
                    width="135"
                    data-testid="sign-up-logo"
                  />
                </NavLink>
              )}
              <main id="content">
                <div id="orejimeElement" />
                {layout === 'funnel' || layout === 'onboarding' ? (
                  <>
                    {mainHeadingWrapper}
                    {children}
                  </>
                ) : (
                  <>
                    {mainTopElement}
                    <div
                      className={cn(
                        styles.content,
                        styles[`content-${layout}`],
                        {
                          [styles['content-logged-out-with-heading']]:
                            layout === 'logged-out' && mainHeading,
                        }
                      )}
                    >
                      {mainHeadingWrapper}
                      {children}
                    </div>
                  </>
                )}
              </main>
              {showFooter && <Footer layout={layout} />}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
