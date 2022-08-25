import { useAdapter } from 'hooks'

import { getVenueLabelsAdapter } from '.'

const useGetVenueLabels = () =>
  useAdapter<SelectOption[], SelectOption[]>(() => getVenueLabelsAdapter())

export default useGetVenueLabels
