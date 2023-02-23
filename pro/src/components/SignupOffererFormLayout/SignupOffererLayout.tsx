import React from 'react'

import SignupBreadcrumb from 'components/SignupBreadcrumb/SignupBreadcrumb'

import styles from './SignupOffererFormLayoutContent.module.scss'

interface ISignupOffererFormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const SignupOffererFormLayout = ({
  children,
}: ISignupOffererFormLayoutProps): JSX.Element => (
  <div className={styles['signup-offerer-layout']}>
    <div className={styles['stepper']}>
      <SignupBreadcrumb />
    </div>
    <div className={styles['content']}>{children}</div>
  </div>
)

export default SignupOffererFormLayout
