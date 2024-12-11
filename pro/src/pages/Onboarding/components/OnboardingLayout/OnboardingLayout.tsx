import cn from 'classnames'
import { type ReactNode } from 'react'

import { Layout } from 'app/App/layout/Layout'

import styles from './OnboardingLayout.module.scss'

interface OnboardingLayoutProps {
  className?: string
  verticallyCentered?: boolean
  children: ReactNode
  stickyActionsAndFooter?: boolean
}

export const OnboardingLayout = ({
  className,
  children,
  verticallyCentered = false,
  stickyActionsAndFooter = true,
}: OnboardingLayoutProps): JSX.Element => {
  return (
    <Layout
      layout={stickyActionsAndFooter ? 'sticky-onboarding' : 'onboarding'}
    >
      <div
        className={cn(
          styles[`onboarding-layout`],
          verticallyCentered ? styles[`vertically-centered`] : undefined,
          className
        )}
      >
        {children}
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OnboardingLayout
