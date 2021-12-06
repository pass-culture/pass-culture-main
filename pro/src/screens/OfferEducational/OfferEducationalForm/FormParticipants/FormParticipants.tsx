import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import { participantsOptions } from './participantsOptions'

const FormParticipants = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Cette offre s'adresse aux élèves de :"
      title="Public visé"
    >
      <FormLayout.Row>
        <CheckboxGroup group={participantsOptions} groupName="participants" />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormParticipants
