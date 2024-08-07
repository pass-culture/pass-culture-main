import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ConfirmedAttachment.module.scss'

export const ConfirmedAttachment = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const { offerer } = useSignupJourneyContext()

  const logNavigation = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: SIGNUP_JOURNEY_STEP_IDS.COMPLETED,
      used: OnboardingFormNavigationAction.WaitingLinkButton,
      categorieJuridiqueUniteLegale: offerer?.legalCategoryCode,
    })
  }
  return (
    <div className={styles['confirmed-attachment-layout']}>
      <div className={styles['title']}>Votre demande a été prise en compte</div>
      <div>
        Un email vous sera envoyé lors de la validation de votre demande. Vous
        aurez alors accès à l’ensemble des fonctionnalités du pass Culture Pro.
      </div>
      <ButtonLink
        onClick={logNavigation}
        className={styles['home-button']}
        variant={ButtonVariant.PRIMARY}
        to="/accueil"
      >
        Accéder à votre espace
      </ButtonLink>
    </div>
  )
}
