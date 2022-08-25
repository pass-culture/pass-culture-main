import { useAdapter } from 'hooks'

import { getVenueTypesAdapter } from '.'

const useGetVenueTypes = () =>
  useAdapter<SelectOption[], SelectOption[]>(() => getVenueTypesAdapter())

export default useGetVenueTypes
