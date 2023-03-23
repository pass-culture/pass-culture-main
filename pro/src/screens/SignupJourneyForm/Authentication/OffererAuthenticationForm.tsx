import React from 'react'

import FormLayout from 'components/FormLayout'
import { TextInput } from 'ui-kit'

import { IOffererFormValues } from '../Offerer/OffererForm'

export interface IOffererAuthenticationFormValues extends IOffererFormValues {
  name: string
  publicName: string
}

const OffererAuthenticationForm = (): JSX.Element => {
  return (
    <FormLayout.Section title="Authentification">
      <FormLayout.Row>
        <TextInput name="siret" label="Numéro de SIRET" type="text" disabled />
        <TextInput name="name" label="Raison sociale" type="text" disabled />
        <TextInput
          name="publicName"
          label="Nom public"
          type="text"
          isOptional
          description="À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public."
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default OffererAuthenticationForm
