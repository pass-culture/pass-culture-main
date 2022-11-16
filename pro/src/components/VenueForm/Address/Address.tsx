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
              acc[add.label.toUpperCase()] = add
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
      handleSelect('', null)
    }
  }, [searchField.value])

  useEffect(() => {
    if (addressesMap[searchField.value] != undefined) {
      handleSelect(searchField.value, addressesMap[searchField.value])
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

  const handleSelect = (
    address: string,
    selectedItem: IAutocompleteItemProps | null
  ) => {
    setFieldValue('addressAutocomplete', searchField.value)
    setFieldValue('address', selectedItem?.extraData.address)
    setFieldValue('postalCode', selectedItem?.extraData.postalCode)
    setFieldValue('city', selectedItem?.extraData.city)
    setFieldValue('latitude', selectedItem?.extraData.latitude)
    setFieldValue('longitude', selectedItem?.extraData.longitude)
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
          ></SelectAutocomplete>
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Address
