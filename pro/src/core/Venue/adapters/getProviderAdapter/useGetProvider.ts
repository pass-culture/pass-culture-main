import { useAdapter } from 'hooks'

import { Providers } from '../../types'

import { getProviderAdapter } from '.'

const useGetProvider = (venueId?: number) =>
  useAdapter<Providers[], Providers[]>(() => getProviderAdapter(venueId))

export default useGetProvider
