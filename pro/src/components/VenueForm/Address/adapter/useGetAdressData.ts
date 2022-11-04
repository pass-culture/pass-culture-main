import { useAdapter } from 'hooks'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { getAdressDataAdapter } from '.'

const useGetAdressData = (search: string) =>
  useAdapter<IAutocompleteItemProps[], IAutocompleteItemProps[]>(() =>
    getAdressDataAdapter(search)
  )

export default useGetAdressData
