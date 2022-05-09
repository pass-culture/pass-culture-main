import { useEffect } from 'react'

const useEffectUnmount = (callback: () => void): void => {
  useEffect(() => () => callback(), [])
}

export default useEffectUnmount
