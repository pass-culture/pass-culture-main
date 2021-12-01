import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import { participantsOptions } from './participantsOptions'

const FormParticipants = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Votre offre s'adresse aux :"
      title="Informations participants"
    >
      <FormLayout.Row>
        <CheckboxGroup group={participantsOptions} name="participants" />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormParticipants
