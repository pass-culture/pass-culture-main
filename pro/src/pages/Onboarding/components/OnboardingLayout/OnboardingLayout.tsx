import cn from 'classnames'
import { type ReactNode } from 'react'

import { Layout } from 'app/App/layout/Layout'
import { Header } from 'components/Header/Header'

import styles from './OnboardingLayout.module.scss'

interface OnboardingLayoutProps {
  className?: string
  showFooter?: boolean
  verticallyCentered?: boolean
  children: ReactNode
}

export const OnboardingLayout = ({
  className,
  showFooter = true,
  children,
  verticallyCentered = false,
}: OnboardingLayoutProps): JSX.Element => {
  return (
    <Layout layout="onboarding" showFooter={showFooter}>
      <Header disableHomeLink={true} />
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

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingLayout
