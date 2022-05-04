import { useEffect } from 'react'

const useEffectMount = (callback: () => void): void => {
  // eslint-disable-next-line
  useEffect(callback, [])
}

export default useEffectMount
