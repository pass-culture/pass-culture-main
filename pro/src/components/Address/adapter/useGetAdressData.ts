import { useAdapter } from 'hooks'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { IAddressParams } from './getAdressDataAdapter'

import { getAdressDataAdapter } from '.'

const useGetAdressData = ({ search, suggestionLimit }: IAddressParams) =>
  useAdapter<IAutocompleteItemProps[], IAutocompleteItemProps[]>(() =>
    getAdressDataAdapter({ search, suggestionLimit })
  )

export default useGetAdressData
