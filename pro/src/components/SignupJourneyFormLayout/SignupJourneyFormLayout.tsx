import classNames from 'classnames'
import React from 'react'

import { SignupJourneyStepper } from 'components/SignupJourneyStepper'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface SignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

const SignupJourneyFormLayout = ({
  children,
}: SignupOffererFormLayoutProps): JSX.Element => {
  return (
    <div
      className={classNames({
        [styles['signup-offerer-layout-wrapper-with-footer']]: true,
      })}
    >
      <SignupJourneyStepper />
      {children}
    </div>
  )
}

export default SignupJourneyFormLayout
