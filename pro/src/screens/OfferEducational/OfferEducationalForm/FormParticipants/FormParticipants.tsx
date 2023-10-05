import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { CheckboxGroup, InfoBox } from 'ui-kit'

import useParticipantsOptions from './useParticipantsOptions'

const FormParticipants = ({
  disableForm,
  isTemplate,
}: {
  disableForm: boolean
  isTemplate: boolean
}): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()

  const defaultPartipantsOptions = useParticipantsOptions(
    values.participants,
    setFieldValue,
    isTemplate
  )

  return (
    <FormLayout.Section title="Participants">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            Le pass Culture à destination du public scolaire s’adresse aux
            élèves de la sixième à la terminale des établissements publics et
            privés sous contrat.
          </InfoBox>
        }
      >
        <CheckboxGroup
          group={defaultPartipantsOptions}
          groupName="participants"
          legend="Cette offre s'adresse aux élèves de :"
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormParticipants
