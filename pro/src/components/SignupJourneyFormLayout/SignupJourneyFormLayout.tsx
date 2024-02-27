import classNames from 'classnames'
import React from 'react'

import { SignupJourneyStepper } from 'components/SignupJourneyStepper'
import useActiveFeature from 'hooks/useActiveFeature'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface SignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

const SignupJourneyFormLayout = ({
  children,
}: SignupOffererFormLayoutProps): JSX.Element => {
  const isNewSideBarNavigation = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')
  return (
    <div
      className={classNames({
        [styles['signup-offerer-layout-wrapper']]: true,
        [styles['signup-offerer-layout-wrapper-with-footer']]:
          isNewSideBarNavigation,
      })}
    >
      <SignupJourneyStepper />
      {children}
    </div>
  )
}

export default SignupJourneyFormLayout
