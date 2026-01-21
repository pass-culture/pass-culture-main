import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import styles from './ConfirmedAttachment.module.scss'

export const ConfirmedAttachment = (): JSX.Element => {
  const { logEvent } = useAnalytics()

  const logNavigation = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: SIGNUP_JOURNEY_STEP_IDS.COMPLETED,
      used: SignupJourneyAction.WaitingLinkButton,
    })
  }
  return (
    <div className={styles['confirmed-attachment-layout']}>
      <h2 className={styles['subtitle']}>
        Votre demande a été prise en compte
      </h2>
      <div>
        Un email vous sera envoyé lors de la validation de votre demande. Vous
        aurez alors accès à l’ensemble des fonctionnalités du pass Culture Pro.
      </div>
      <Button
        as="a"
        onClick={logNavigation}
        className={styles['home-button']}
        variant={ButtonVariant.PRIMARY}
        to="/accueil"
        label="Accéder à votre espace"
      />
    </div>
  )
}
