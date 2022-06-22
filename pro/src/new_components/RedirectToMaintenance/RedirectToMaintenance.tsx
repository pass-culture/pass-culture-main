// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html

import { URL_FOR_MAINTENANCE } from 'utils/config'
import { useEffect } from 'react'

const RedirectToMaintenance = (): null => {
  useEffect(() => {
    window.location.href = URL_FOR_MAINTENANCE as string
  }, [])
  return null
}

export default RedirectToMaintenance
