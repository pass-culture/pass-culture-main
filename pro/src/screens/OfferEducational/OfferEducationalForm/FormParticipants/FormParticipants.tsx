import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import { CheckboxGroup, InfoBox } from 'ui-kit'

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

  const isCLG6Active = useActiveFeature('WIP_ADD_CLG_6_5_COLLECTIVE_OFFER')

  return (
    <FormLayout.Section title="Participants">
      <FormLayout.Row
        sideComponent={
          <InfoBox
            type="info"
            text={`Le pass Culture à destination du public scolaire s’adresse aux élèves de la ${
              isCLG6Active ? 'sixième' : 'quatrième'
            } à la terminale des établissements publics et privés sous contrat.`}
          />
        }
      >
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
