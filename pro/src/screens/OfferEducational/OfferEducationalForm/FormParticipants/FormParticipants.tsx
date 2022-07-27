import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import { participantsOptions } from './participantsOptions'

const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => (
  <FormLayout.Section title="Participants">
    <FormLayout.Row>
      <CheckboxGroup
        group={participantsOptions}
        groupName="participants"
        legend="Cette offre s'adresse aux élèves de :"
        disabled={disableForm}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormParticipants
