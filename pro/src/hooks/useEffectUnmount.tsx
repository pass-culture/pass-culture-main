import { useEffect } from 'react'

const useEffectUnmount = (callback: () => void): void => {
  useEffect(
    () => () => callback(),
    [] // eslint-disable-line
  )
}

export default useEffectUnmount
