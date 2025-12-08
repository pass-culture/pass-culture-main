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

import styles from './OnboardingLayout.module.scss'

interface OnboardingLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
  /**
   * When StickyActionBar is rendered within the children,
   * Footer needs to have a special margin-bottom to be visible
   * above it.
   */
  isStickyActionBarInChild?: boolean
  /**
   * A property to vertically center contents, only
   * available for entry screens.
   */
  verticallyCentered?: boolean
  /**
   * Entry screens (screens that preceeds a redirection,
   * or a form) have extra paddings and can be
   * vertically centered.
   * FIXME: this should be removed in favor of an unique
   * UI in the context of an onboarding.
   */
  isEntryScreen?: boolean
}

export const OnboardingLayout = ({
  children,
  mainHeading,
  isStickyActionBarInChild = false,
  verticallyCentered = false,
  isEntryScreen = false,
}: OnboardingLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)

  const mainHeadingWrapper = (
    <MainHeading
      className={cn(styles['main-heading'], {
        [styles['main-heading-centered']]: isEntryScreen,
      })}
      mainHeading={mainHeading}
    />
  )

  const layoutVariant = isStickyActionBarInChild
    ? 'sticky-onboarding'
    : 'onboarding'

  return (
    <div className={styles.layout}>
      <SkipLinks />
      {currentUser?.isImpersonated && (
        <ConnectedAsAside currentUser={currentUser} />
      )}
      <Header disableHomeLink />
      <div
        className={cn(styles['page-layout'], {
          [styles['page-layout-connect-as']]: currentUser?.isImpersonated,
        })}
      >
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div
            className={cn(
              styles['content-container'],
              styles[`content-container-${layoutVariant}`]
            )}
          >
            <main id="content">
              <div
                className={cn(
                  styles['content'],
                  styles[`content-${layoutVariant}`]
                )}
              >
                {isEntryScreen ? (
                  <div
                    className={cn(
                      styles[`onboarding-layout`],
                      verticallyCentered
                        ? styles[`vertically-centered`]
                        : undefined
                    )}
                  >
                    {mainHeadingWrapper}
                    {children}
                  </div>
                ) : (
                  <>
                    {mainHeadingWrapper}
                    {children}
                  </>
                )}
              </div>
            </main>
            <Footer
              layout={
                isStickyActionBarInChild ? 'sticky-onboarding' : 'onboarding'
              }
            />
          </div>
        </div>
      </div>
    </div>
  )
}
