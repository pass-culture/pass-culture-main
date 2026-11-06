import { redirect } from 'react-router'

import { rootStore } from '@/commons/store/store'

export const mustHaveSelectedNatureAndFormat = () => {
  const { nature, format } = rootStore.getState().nfd

  if (!nature || !format) {
    return redirect('/offre/individuelle/v2/creation/nature-format-domaine')
  }

  return null
}
