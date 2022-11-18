import { useField, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout'
import SelectAutocomplete from 'ui-kit/form/SelectAutoComplete2/SelectAutocomplete'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { IVenueFormValues } from '../types'

import { getAdressDataAdapter } from './adapter'
const Address = () => {
  const { setFieldValue } = useFormikContext<IVenueFormValues>()
  const [options, setOptions] = useState<SelectOption[]>([])
  const [addressesMap, setAddressesMap] = useState<
    Record<string, IAutocompleteItemProps>
  >({})
  const [searchField] = useField('search-addressAutocomplete')
  const [selectedField] = useField('addressAutocomplete')
  useEffect(() => {
    setOptions([{ label: selectedField.value, value: selectedField.value }])
  }, [])

  useEffect(() => {
    if (searchField.value.length >= 3) {
      getSuggestions(searchField.value).then(response => {
        setAddressesMap(
          response.reduce<Record<string, IAutocompleteItemProps>>(
            (acc, add: IAutocompleteItemProps) => {
              acc[add.label] = add
              return acc
            },
            {}
          )
        )
        setOptions(
          response.map(item => {
            return {
              value: String(item.value),
              label: item.label,
            }
          })
        )
      })
    } else if (searchField.value.length === 0) {
      setOptions([])
      handleAddressSelect(setFieldValue, undefined, searchField)
    }
  }, [searchField.value])

  useEffect(() => {
    if (addressesMap[searchField.value] != undefined) {
      handleAddressSelect(
        setFieldValue,
        addressesMap[searchField.value],
        searchField
      )
    }
  }, [selectedField.value])

  /* istanbul ignore next: DEBT, TO FIX */
  const getSuggestions = async (search: string) => {
    if (search) {
      const response = await getAdressDataAdapter(search)
      if (response.isOk) {
        return response.payload
      }
    }
    return []
  }

  return (
    <>
      <FormLayout.Section
        title="Adresse du lieu"
        description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
      >
        <FormLayout.Row>
          <SelectAutocomplete
            fieldName="addressAutocomplete"
            label="Adresse postale"
            placeholder="Entrez votre adresse et sélectionnez une suggestion"
            options={options}
            hideArrow={true}
            resetOnOpen={false}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
export const handleAddressSelect = (
  setFieldValue: any,
  selectedItem?: IAutocompleteItemProps,
  searchField?: any
) => {
  setFieldValue('address', selectedItem?.extraData.address)
  if (searchField) {
    setFieldValue('addressAutocomplete', searchField?.value)
  }
  setFieldValue('postalCode', selectedItem?.extraData.postalCode)
  setFieldValue('city', selectedItem?.extraData.city)
  setFieldValue('latitude', selectedItem?.extraData.latitude)
  setFieldValue('longitude', selectedItem?.extraData.longitude)
}

export default Address
