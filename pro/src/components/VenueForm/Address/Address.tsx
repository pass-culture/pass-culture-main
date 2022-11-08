import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'
import TextInputAutocomplete from 'ui-kit/form/TextInputAutocomplete'

import { IVenueFormValues } from '../types'

import { getAdressDataAdapter } from './adapter'

const Address = () => {
  const { setFieldValue } = useFormikContext<IVenueFormValues>()

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

  const handleSelect = (selectedItem: IAutocompleteItemProps) => {
    setFieldValue('address', selectedItem.extraData.address)
    setFieldValue('postalCode', selectedItem.extraData.postalCode)
    setFieldValue('city', selectedItem.extraData.city)
    setFieldValue('latitude', selectedItem.extraData.latitude)
    setFieldValue('longitude', selectedItem.extraData.longitude)
  }

  return (
    <>
      <FormLayout.Section
        title="Adresse du lieu"
        description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
      >
        <FormLayout.Row>
          <TextInputAutocomplete
            fieldName="addressAutocomplete"
            label="Adresse postale"
            placeholder={'Entrez votre adresse et sélectionnez une suggestion'}
            getSuggestions={getSuggestions}
            onSelectCustom={handleSelect}
            useDebounce
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Address
