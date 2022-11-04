import { useLocation } from 'react-router'

import { STEP_NAMES } from '../constants'

const useActiveStep = (): string => {
  const location = useLocation()
  const matchStepNamePath: RegExpMatchArray | null =
    location.pathname.match(/[a-z]+$/)
  let newActiveStepName: string =
    matchStepNamePath !== null ? matchStepNamePath[0] : ''
  if (!STEP_NAMES.includes(newActiveStepName)) {
    newActiveStepName = STEP_NAMES[0]
  }
  return newActiveStepName
}

export default useActiveStep
