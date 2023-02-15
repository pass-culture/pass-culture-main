import { TSearchFilters } from 'core/Offers/types'
import { useAdapter } from 'hooks'

import { IPayload } from './getFilteredOffersAdapter'

import { getFilteredOffersAdapter } from '.'

const useGetFilteredOffersAdapter = (apiFilters: TSearchFilters) =>
  useAdapter<IPayload, IPayload>(() => getFilteredOffersAdapter(apiFilters))

export default useGetFilteredOffersAdapter
