import cn from 'classnames'
import { useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { getUserDefaultPath } from '@/app/AppRouter/utils/getUserDefaultPath'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import styles from './ConfirmedAttachment.module.scss'

export const ConfirmedAttachment = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()

  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const logNavigation = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      to: SIGNUP_JOURNEY_STEP_IDS.COMPLETED,
      used: SignupJourneyAction.WaitingLinkButton,
    })

    navigate(getUserDefaultPath())
  }
  return (
    <div
      className={cn({
        [styles['confirmed-attachment-container']]: isSignupSimulationEnabled,
      })}
    >
      <div>
        <MainHeading
          className={styles['main-heading']}
          mainHeading="Votre demande a été envoyée"
        />
        <p className={styles['subheading-description']}>
          Nos équipes valideront votre rattachement par email. Vous aurez alors
          accès à l'ensemble des fonctionnalités du pass Culture Pro.
        </p>
      </div>
      <Button
        onClick={logNavigation}
        variant={ButtonVariant.PRIMARY}
        label="Accéder à mon espace"
      />
    </div>
  )
}
