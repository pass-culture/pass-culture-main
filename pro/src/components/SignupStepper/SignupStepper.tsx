import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import { SIGNUP_STEP_IDS } from './constants'
import styles from './SignupStepper.module.scss'

export const SignupStepper = () => {
  const activeStep = useActiveStep()

  const steps: Step[] = [
    {
      id: SIGNUP_STEP_IDS.ACCOUNT_CREATION,
      label: 'Votre compte',
    },
    {
      id: SIGNUP_STEP_IDS.STRUCTURE_IDENTIFICATION,
      label: 'Votre structure',
    },
    {
      id: SIGNUP_STEP_IDS.ACTIVITY,
      label: 'Votre activité',
    },
    {
      id: SIGNUP_STEP_IDS.VALIDATION,
      label: 'Validation',
    },
  ]

  const activeStepIndex = steps.findIndex(
    ({ id }) => id === (activeStep as SIGNUP_STEP_IDS)
  )

  const signupSteps = steps.map((step, index) => ({
    ...step,
    disabled: index > activeStepIndex,
  }))

  const stepsIds = signupSteps.map((step) => step.id)

  if (!stepsIds.includes(activeStep)) {
    return null
  }

  return (
    <Stepper
      activeStep={activeStep}
      steps={signupSteps}
      className={styles['signup-stepper']}
    />
  )
}
