import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextArea, TextInput } from 'ui-kit'

const Informations = (): JSX.Element => {
  return (
    <FormLayout.Section title="Informations générales">
      <FormLayout.Row>
        <TextInput
          countCharacters
          label="Titre de l'offre"
          maxLength={90}
          name="title"
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea
          countCharacters
          isOptional
          label="Description"
          maxLength={1000}
          name="description"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default Informations
