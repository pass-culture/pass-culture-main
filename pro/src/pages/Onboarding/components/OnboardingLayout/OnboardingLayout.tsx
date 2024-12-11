import cn from 'classnames'
import { type ReactNode } from 'react'

import { Layout } from 'app/App/layout/Layout'
// import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { Header } from 'components/Header/Header'
// import fullLeftIcon from 'icons/full-left.svg'
// import fullRightIcon from 'icons/full-right.svg'
// import { Button } from 'ui-kit/Button/Button'
// import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

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
