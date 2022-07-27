// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html

import { useEffectMount } from 'hooks'
import { URL_FOR_MAINTENANCE } from 'utils/config'

const RedirectToMaintenance = (): null => {
  useEffectMount(() => {
    window.location.href = URL_FOR_MAINTENANCE as string
  })
  return null
}

export default RedirectToMaintenance
