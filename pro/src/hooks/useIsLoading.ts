import { useEffect, useState } from 'react'

// await new Promise(resolve => setTimeout(resolve, 1000))

const useIsLoading = (loadingStates: boolean[], delayInMillisecond = 500) => {
  const [isLoading, setIsLoading] = useState<boolean>(
    !loadingStates.every(v => v === false)
  )
  const [timerId, setTimerId] = useState<ReturnType<typeof setTimeout>>()
  const [canStopLoading, setCanStopLoading] = useState(true)

  const startTimer = () => {
    setTimerId(
      setTimeout(() => {
        setCanStopLoading(true)
      }, delayInMillisecond)
    )
  }

  useEffect(() => {
    const newIsLoading = !loadingStates.every(v => v === false)
    if (newIsLoading && !timerId) {
      setCanStopLoading(false)
      setIsLoading(true)
      startTimer()
    }
  }, [loadingStates, timerId])

  useEffect(() => {
    const newIsLoading = !loadingStates.every(v => v === false)
    if (isLoading && !newIsLoading && canStopLoading) {
      setIsLoading(false)
      clearTimeout(timerId)
      setTimerId(undefined)
    }
  }, [loadingStates, isLoading, canStopLoading])

  return isLoading
}

export default useIsLoading
