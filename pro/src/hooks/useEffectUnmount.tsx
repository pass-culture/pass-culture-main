import { useEffect } from 'react'

const useEffectUnmount = (callback: () => void): void => {
  useEffect(() => () => callback(), [callback])
}

export default useEffectUnmount
