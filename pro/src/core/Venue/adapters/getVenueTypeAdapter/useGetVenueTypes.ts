import { SelectOption } from 'custom_types/form'
import { useAdapter } from 'hooks'

import { getVenueTypesAdapter } from '.'

const useGetVenueTypes = () =>
  useAdapter<SelectOption[], SelectOption[]>(() => getVenueTypesAdapter())

export default useGetVenueTypes
