import React from 'react'

import { SignupJourneyBreadcrumb } from 'components/SignupJourneyBreadcrumb'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface ISignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

const SignupJourneyFormLayout = ({
  children,
}: ISignupOffererFormLayoutProps): JSX.Element => (
  <div className={styles['signup-offerer-layout-wrapper']}>
    <SignupJourneyBreadcrumb />
    {children}
  </div>
)

export default SignupJourneyFormLayout
