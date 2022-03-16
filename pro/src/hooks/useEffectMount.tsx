import { useEffect } from 'react'

const useEffectMount = (callback: () => void): void => {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(callback, [])
}

export default useEffectMount
