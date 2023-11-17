import React from 'react'

import { SignupJourneyStepper } from 'components/SignupJourneyStepper'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface SignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

const SignupJourneyFormLayout = ({
  children,
}: SignupOffererFormLayoutProps): JSX.Element => (
  <div className={styles['signup-offerer-layout-wrapper']}>
    <SignupJourneyStepper />
    {children}
  </div>
)

export default SignupJourneyFormLayout
