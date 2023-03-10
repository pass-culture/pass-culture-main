import { useAdapter } from 'hooks'

import getVenuesOfOffererFromSiretAdapter from './getVenuesOfOffererFromSiretAdapter'

const useGetVenuesOfOffererFromSiretAdapter = (siret: string) =>
  useAdapter(() => getVenuesOfOffererFromSiretAdapter(siret))

export default useGetVenuesOfOffererFromSiretAdapter
