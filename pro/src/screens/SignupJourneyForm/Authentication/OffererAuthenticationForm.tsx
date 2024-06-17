import React from 'react'

import { AddressSelect } from 'components/Address/Address'
import { Address } from 'components/Address/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { OffererFormValues } from '../Offerer/OffererForm'

export interface OffererAuthenticationFormValues
  extends OffererFormValues,
    Address {
  name: string
  publicName: string
  addressAutocomplete: string
  'search-addressAutocomplete': string
}

export const OffererAuthenticationForm = (): JSX.Element => {
  return (
    <FormLayout.Section>
      <h1>Identification</h1>
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
        <AddressSelect
          description="À modifier si l’adresse postale de votre structure est différente de la raison sociale."
          suggestionLimit={5}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
