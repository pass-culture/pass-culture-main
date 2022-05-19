import { useEffect, useRef } from 'react'

import { logEventType } from './useAnalytics'

// (mageoffray, 2022-05-25) This hook should only be used to log events on form leaving (by closing the current tab).
// beforeunload is supported by all modern browsers but some functions are not executed in some browsers.
// https://caniuse.com/?search=beforeunload
const useLogEventOnUnload = (logEvent: () => logEventType) => {
  const logEventRef = useRef(logEvent)
  useEffect(() => {
    const onUnload = () => logEventRef.current()
    window.addEventListener('beforeunload', onUnload)
    return () => {
      window.removeEventListener('beforeunload', onUnload)
    }
  }, [logEventRef])
}

export default useLogEventOnUnload
