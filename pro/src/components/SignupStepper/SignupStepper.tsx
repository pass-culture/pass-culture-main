import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { type StepItem, Stepper } from '@/design-system/Stepper/Stepper'

import { SIGNUP_STEP_IDS } from './constants'

export const SignupStepper = () => {
  const activeStep = useActiveStep()

  const steps: StepItem[] = [
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

  const stepsIds = steps.map((step) => step.id)

  if (!stepsIds.includes(activeStep)) {
    return null
  }

  return <Stepper activeStep={activeStep} steps={steps} />
}
