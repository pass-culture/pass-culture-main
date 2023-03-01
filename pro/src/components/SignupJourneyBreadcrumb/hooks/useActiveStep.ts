import { useLocation } from 'react-router-dom-v5-compat'

const useActiveStep = (): string => {
  const location = useLocation()
  const matchStepNamePath: RegExpMatchArray | null =
    location.pathname.match(/[a-z]+$/)
  const newActiveStepName: string =
    matchStepNamePath !== null ? matchStepNamePath[0] : ''
  return newActiveStepName
}

export default useActiveStep
