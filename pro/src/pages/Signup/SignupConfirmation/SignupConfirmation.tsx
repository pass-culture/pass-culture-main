import cn from 'classnames'
import { useLocation } from 'react-router'

import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'

import styles from './SignupConfirmation.module.scss'

export const SignupConfirmation = () => {
  const location = useLocation()
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  return (
    <section
      className={cn({
        [styles['signup-confirmation-container']]: isSignupSimulationEnabled,
      })}
    >
      {isSignupSimulationEnabled && (
        <MainHeading mainHeading="Validez votre adresse email" />
      )}
      <p className={styles['signup-confirmation']}>
        Cliquez sur le lien envoyé par email
        {location.state?.email && (
          <>
            {' '}
            à<br />
            <b>{location.state.email}</b>
          </>
        )}
      </p>
      <ReSendEmailCallout hideLink />
    </section>
  )
}
