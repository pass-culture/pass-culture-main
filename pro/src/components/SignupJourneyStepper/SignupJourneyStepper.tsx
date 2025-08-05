import { useLocation } from 'react-router'

import { useAnalytics } from 'app/App/analytics/firebase'
import { DEFAULT_ACTIVITY_VALUES } from 'commons/context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveStep } from 'commons/hooks/useActiveStep'
import { DEFAULT_OFFERER_FORM_VALUES } from 'components/SignupJourneyForm/Offerer/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { Step, Stepper } from 'components/Stepper/Stepper'

import { SIGNUP_JOURNEY_STEP_IDS } from './constants'
import styles from './SignupJourneyStepper.module.scss'

export const SignupJourneyStepper = () => {
  const { activity, offerer } = useSignupJourneyContext()

  const { logEvent } = useAnalytics()

  const isActivityStepDisabled =
    activity === null || activity === DEFAULT_ACTIVITY_VALUES

  const isOffererStepDisabled =
    offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES

  const everyStepActivated = !isActivityStepDisabled && !isOffererStepDisabled

  const location = useLocation()
  const activeStep = useActiveStep()

  const logBreadcrumbClick = (to: SIGNUP_JOURNEY_STEP_IDS, stepUrl: string) => {
    if (stepUrl.indexOf(activeStep) === -1) {
      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to,
        used: OnboardingFormNavigationAction.Breadcrumb,
      })
    }
  }

  const signupJourneyBreadcrumbSteps: Step[] = [
    {
      id: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      label: 'Vos informations',
      url: '/inscription/structure/identification',
      onClick: () =>
        logBreadcrumbClick(
          SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
          '/inscription/structure/identification'
        ),
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
      label: 'Votre activité',
      url: isActivityStepDisabled
        ? undefined
        : '/inscription/structure/activite',
      onClick: () => {
        if (!isActivityStepDisabled) {
          logBreadcrumbClick(
            SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
            '/inscription/structure/activite'
          )
        }
      },
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
      label: 'Validation',
      url: !everyStepActivated
        ? undefined
        : '/inscription/structure/confirmation',
      onClick: () => {
        if (everyStepActivated) {
          logBreadcrumbClick(
            SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
            '/inscription/structure/confirmation'
          )
        }
      },
    },
  ]

  const stepsIds = signupJourneyBreadcrumbSteps.map((step) => step.id)

  if (!stepsIds.includes(activeStep)) {
    return <></>
  }

  return (
    <Stepper
      activeStep={activeStep}
      steps={signupJourneyBreadcrumbSteps}
      className={styles['signup-stepper']}
    />
  )
}
