import { useEffect } from 'react'

const useEffectUnmount = (callback: () => void): void => {
  useEffect(
    () => () => callback(),
    [] // eslint-disable-line react-hooks/exhaustive-deps
  )
}

export default useEffectUnmount
