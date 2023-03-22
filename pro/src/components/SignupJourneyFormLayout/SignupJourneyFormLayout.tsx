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
    <div className={styles['signup-offerer-layout']}>
      <div className={styles['stepper']}>
        <SignupJourneyBreadcrumb />
      </div>
      <div className={styles['content']}>{children}</div>
    </div>
  </div>
)

export default SignupJourneyFormLayout
