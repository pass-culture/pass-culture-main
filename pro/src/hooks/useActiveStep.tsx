import { useLocation } from 'react-router-dom'

const useActiveStep = (steps?: string[]): string => {
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

export default useActiveStep
