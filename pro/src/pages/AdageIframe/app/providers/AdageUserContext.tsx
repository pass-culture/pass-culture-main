import { createContext } from 'react'

import { AuthenticatedResponse } from 'apiClient/adage'

type AdageUserContextType = {
  adageUser?: AuthenticatedResponse | null
}

export const AdageUserContext = createContext<AdageUserContextType>({
  adageUser: null,
})
