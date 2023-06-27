import React from 'react'

import { SignupJourneyBreadcrumb } from 'components/SignupJourneyBreadcrumb'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface SignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

const SignupJourneyFormLayout = ({
  children,
}: SignupOffererFormLayoutProps): JSX.Element => (
  <div className={styles['signup-offerer-layout-wrapper']}>
    <SignupJourneyBreadcrumb />
    {children}
  </div>
)

export default SignupJourneyFormLayout
