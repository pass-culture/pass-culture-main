import { useFormikContext } from 'formik'
import React from 'react'

import { StudentLevels } from 'apiClient/adage'
import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
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

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const filteredParticipantsOptions = isMarseilleEnabled
    ? defaultPartipantsOptions
    : defaultPartipantsOptions.filter(
        (option) =>
          option.name !==
            `participants.${StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_MATERNELLE}` &&
          option.name !==
            `participants.${StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_PRIMAIRE}`
      )

  return (
    <FormLayout.Section title="Participants">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            {isMarseilleEnabled
              ? `Dans le cadre du projet Marseille en Grand, les écoles primaires
            innovantes du territoire marseillais bénéficient d’un budget pour
            financer des projets d’EAC avec leurs élèves.`
              : `Le pass Culture à destination du public scolaire s’adresse aux
            élèves de la sixième à la terminale des établissements publics et
            privés sous contrat.`}
          </InfoBox>
        }
      >
        <CheckboxGroup
          group={filteredParticipantsOptions}
          groupName="participants"
          legend="Cette offre s'adresse aux élèves de :"
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormParticipants
