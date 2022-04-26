import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextInput } from 'ui-kit'

const OfferIndividualForm = () => {
  return (
    <FormLayout>
      <FormLayout.Section title="Informations">
        <TextInput label="Champ de démo" name="name" />
      </FormLayout.Section>

      <FormLayout.Section title="Informations pratique">
        <p>@Todo information pratique section</p>
      </FormLayout.Section>

      <FormLayout.Section title="Accessiblité">
        <p>@Todo Accessiblité section</p>
      </FormLayout.Section>
    </FormLayout>
  )
}

export default OfferIndividualForm
