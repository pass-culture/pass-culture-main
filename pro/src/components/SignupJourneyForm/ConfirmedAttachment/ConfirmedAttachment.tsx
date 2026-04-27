import { useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { getUserDefaultPath } from '@/app/AppRouter/utils/getUserDefaultPath'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import styles from './ConfirmedAttachment.module.scss'

export const ConfirmedAttachment = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()

  const logNavigation = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: SIGNUP_JOURNEY_STEP_IDS.COMPLETED,
      used: SignupJourneyAction.WaitingLinkButton,
    })

    navigate(getUserDefaultPath())
  }
  return (
    <div className={styles['confirmed-attachment-layout']}>
      <div>
        <h2 className={styles['title']}>Votre demande a été envoyée</h2>
        <div className={styles['subtitle']}>
          Nos équipes valideront votre rattachement par email. Vous aurez alors
          accès à l'ensemble des fonctionnalités du pass Culture Pro.
        </div>
      </div>
      <Button
        onClick={logNavigation}
        variant={ButtonVariant.PRIMARY}
        label="Accéder à votre espace"
      />
    </div>
  )
}
