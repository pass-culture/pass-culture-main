import { useLocation } from 'react-router'

export const useActiveStep = (steps?: readonly string[]): string => {
  const location = useLocation()
  const pathname = location.pathname
  const pathParts = pathname.split('/')
  const lastPathPart = pathParts[pathParts.length - 1]
  let newActiveStepName: string = lastPathPart
  if (steps) {
    if (!steps.includes(newActiveStepName)) {
      newActiveStepName = steps[0]
    }
  }

  return newActiveStepName
}
