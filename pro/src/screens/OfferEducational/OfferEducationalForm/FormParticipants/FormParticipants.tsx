import { useFormikContext } from 'formik'
import React from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import { participantsOptions } from './participantsOptions'
import useParicipantUpdates from './useParticipantUpdates'

const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const handleParticipantsChange = (
    newParticipants: IOfferEducationalFormValues['participants']
  ) => setFieldValue('participants', newParticipants)

  useParicipantUpdates(values.participants, handleParticipantsChange)

  return (
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
}

export default FormParticipants
