import { useLocation } from 'react-router'

import { OFFER_WIZARD_STEP_IDS } from '../constants'

const useActiveStep = (): string => {
  const location = useLocation()
  const matchStepNamePath: RegExpMatchArray | null =
    location.pathname.match(/[a-z]+$/)
  let newActiveStepName: string =
    matchStepNamePath !== null ? matchStepNamePath[0] : ''

  const possibleSteps: string[] = Object.values(OFFER_WIZARD_STEP_IDS)
  if (!possibleSteps.includes(newActiveStepName)) {
    newActiveStepName = OFFER_WIZARD_STEP_IDS.INFORMATIONS
  }
  return newActiveStepName
}

export default useActiveStep
