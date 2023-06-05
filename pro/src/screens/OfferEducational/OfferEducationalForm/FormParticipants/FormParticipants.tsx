import isBefore from 'date-fns/isBefore'
import { useFormikContext } from 'formik'
import React from 'react'

import {
  GetCollectiveOfferCollectiveStockResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import { Banner, CheckboxGroup, InfoBox } from 'ui-kit'

import useParticipantsOptions from './useParticipantsOptions'

const FormParticipants = ({
  disableForm,
  offerStock,
}: {
  disableForm: boolean
  offerStock?: GetCollectiveOfferCollectiveStockResponseModel | null
}): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const isCLG6Active = useActiveFeature('WIP_ADD_CLG_6_5_COLLECTIVE_OFFER')
  const isBeforeSeptembre1st =
    offerStock?.beginningDatetime &&
    isBefore(
      new Date(offerStock.beginningDatetime),
      new Date('2023-09-01T00:00:00Z')
    )
  const defaultPartipantsOptions = useParticipantsOptions(
    values.participants,
    setFieldValue
  )
  const filteredParticipantsOptions =
    isCLG6Active && !isBeforeSeptembre1st
      ? defaultPartipantsOptions
      : defaultPartipantsOptions.filter(
          x =>
            x.name !== `participants.${StudentLevels.COLL_GE_6E}` &&
            x.name !== `participants.${StudentLevels.COLL_GE_5E}`
        )

  return (
    <FormLayout.Section title="Participants">
      {isCLG6Active && (
        <Banner type="attention">
          À partir du 1er septembre 2023, le pass Culture est étendu aux classes
          de 6e et 5e. Grâce au déploiement du dispositif, vous pouvez désormais
          créer des offres pour ces classes pour l’année scolaire 2023-2024.
        </Banner>
      )}
      <FormLayout.Row
        sideComponent={
          !isCLG6Active ? (
            <InfoBox>
              Le pass Culture à destination du public scolaire s’adresse aux
              élèves de la {isCLG6Active ? 'sixième' : 'quatrième'} à la
              terminale des établissements publics et privés sous contrat.
            </InfoBox>
          ) : null
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
