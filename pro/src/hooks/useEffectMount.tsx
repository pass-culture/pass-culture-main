import { useEffect } from 'react'

const useEffectMount = (callback: () => void): void => {
  useEffect(callback, [])
}

export default useEffectMount
