import { useFormikContext } from 'formik'
import React from 'react'

import { StudentLevels } from 'apiClient/adage'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { useParticipantsOptions } from './useParticipantsOptions'

export const FormParticipants = ({
  disableForm,
  isTemplate,
}: {
  disableForm: boolean
  isTemplate: boolean
}): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const defaultPartipantsOptions = useParticipantsOptions(
    values.participants,
    setFieldValue,
    isTemplate,
    isMarseilleEnabled
  )

  const filteredParticipantsOptions = isMarseilleEnabled
    ? defaultPartipantsOptions
    : defaultPartipantsOptions.filter(
        (option) =>
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_MATERNELLE}` &&
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_CP_CE1_CE2}` &&
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_CM1_CM2}`
      )

  return (
    <FormLayout.Section title="Participants">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            {isMarseilleEnabled
              ? `Dans le cadre du plan Marseille en Grand et du Conseil national de la refondation dans son volet éducation "Notre école, faisons-la ensemble", les écoles primaires innovantes du territoire marseillais bénéficient d’un budget pour financer des projets d’EAC avec leurs élèves.`
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
