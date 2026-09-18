import cn from 'classnames'
import { useLocation } from 'react-router'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'
import { Title } from '@/ui-kit/Title/Title'

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
        <Title
          level="1"
          title="Validez votre adresse email"
          marginBottom="xxl"
        />
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
