import { useLocation } from 'react-router'

import { SIGNUP_STEP_IDS } from '../constants'

const useActiveStep = (): string => {
  const location = useLocation()
  const matchStepNamePath: RegExpMatchArray | null =
    location.pathname.match(/[a-z]+$/)
  let newActiveStepName: string =
    matchStepNamePath !== null ? matchStepNamePath[0] : ''

  const possibleSteps: string[] = Object.values(SIGNUP_STEP_IDS)
  if (!possibleSteps.includes(newActiveStepName)) {
    newActiveStepName = SIGNUP_STEP_IDS.AUTHENTICATION
  }
  return newActiveStepName
}

export default useActiveStep
