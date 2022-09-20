import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit'

import { IOfferIndividualFormValues } from '../types'

const OptionDuo = (): JSX.Element | null => {
  const {
    values: { subCategoryFields },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(() => {
    !subCategoryFields.includes('isDuo')
      ? setFieldValue('isDuo', false)
      : setFieldValue('isDuo', true)
  }, [subCategoryFields])

  if (!subCategoryFields.includes('isDuo')) {
    return null
  }

  return (
    <FormLayout.Section title="Réservations “duo“">
      <FormLayout.Row>
        <Checkbox
          label="Accepter les réservations “duo“"
          description="En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l‘accompagnateur."
          name="isDuo"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default OptionDuo
