import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import { REGISTRATION_STEP_IDS } from './constants'
import styles from './RegistrationStepper.module.scss'

export const RegistrationStepper = () => {
  const activeStep = useActiveStep()

  const steps: Step[] = [
    {
      id: REGISTRATION_STEP_IDS.SIGNUP,
      label: 'Votre compte',
    },
    {
      id: REGISTRATION_STEP_IDS.STRUCTURE,
      label: 'Votre structure',
    },
    {
      id: REGISTRATION_STEP_IDS.ACTIVITY,
      label: 'Votre activité',
    },
    {
      id: REGISTRATION_STEP_IDS.VALIDATION,
      label: 'Validation',
    },
  ]

  const activeStepIndex = steps.findIndex(
    ({ id }) => id === (activeStep as REGISTRATION_STEP_IDS)
  )

  const registrationSteps = steps.map((step, index) => ({
    ...step,
    disabled: index > activeStepIndex,
  }))

  const stepsIds = registrationSteps.map((step) => step.id)

  if (!stepsIds.includes(activeStep)) {
    return null
  }

  return (
    <Stepper
      activeStep={activeStep}
      steps={registrationSteps}
      className={styles['signup-stepper']}
    />
  )
}
