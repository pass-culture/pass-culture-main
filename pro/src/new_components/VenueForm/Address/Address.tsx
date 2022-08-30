import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { InfoBox, TextArea } from 'ui-kit'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'
import TextInputAutocomplete from 'ui-kit/form/TextInputAutocomplete'

import { IVenueFormValues } from '../types'

import { getAdressDataAdapter } from './adapter'

const Address = () => {
  const { setFieldValue } = useFormikContext<IVenueFormValues>()

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
            label="Adresse"
            getSuggestions={getSuggestions}
            onSelectCustom={handleSelect}
            useDebounce
          />
        </FormLayout.Row>
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="important"
              text="Si vous ne trouvez pas l’adresse dans la liste ci-dessus, choisissez celle qui est la plus proche de votre lieu et indiquez 
ci-contre l'adresse précise."
            />
          }
        >
          <TextArea
            label="Complément d'adresse"
            name="additionalAddress"
            isOptional
            maxLength={500}
            countCharacters
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Address
