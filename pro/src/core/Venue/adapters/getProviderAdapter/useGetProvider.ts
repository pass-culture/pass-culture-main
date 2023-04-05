import { useAdapter } from 'hooks'

import { IProviders } from '../../types'

import { getProviderAdapter } from '.'

const useGetProvider = (venueId?: number) =>
  useAdapter<IProviders[], IProviders[]>(() => getProviderAdapter(venueId))

export default useGetProvider
