import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextInput } from 'ui-kit'

const Informations = () => {
  return (
    <>
      <FormLayout.Section title="Informations lieu">
        <FormLayout.Row>
          <TextInput name="publicName" label="Nom d’usage du lieu:" />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Informations
