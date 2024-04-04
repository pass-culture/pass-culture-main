import { useFormikContext } from 'formik'
import React from 'react'

import {
  CollectiveBookingStatus,
  GetEducationalOffererResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import FormLayout from 'components/FormLayout'
import {
  applyVenueDefaultsToFormValues,
  OfferEducationalFormValues,
  isCollectiveOffer,
  Mode,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import { Banner, Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

import styles from './FormVenue.module.scss'
interface FormVenueProps {
  userOfferers: GetEducationalOffererResponseModel[]
  venuesOptions: SelectOption[]
  isEligible: boolean | undefined
  mode: Mode
  isOfferCreated: boolean
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel

  onChangeOfferer: (event: string) => void
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  isEligible,
  mode,
  isOfferCreated,
  offer,
  onChangeOfferer,
}: FormVenueProps): JSX.Element => {
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.lastBookingStatus
    : null
  const disableOfferSelection = mode !== Mode.CREATION || isOfferCreated
  const disabledBookingStatus = [
    CollectiveBookingStatus.USED,
    CollectiveBookingStatus.REIMBURSED,
  ]
  const disableVenueSelection =
    mode === Mode.READ_ONLY ||
    (lastBookingStatus !== undefined &&
      lastBookingStatus !== null &&
      disableOfferSelection &&
      disabledBookingStatus.includes(lastBookingStatus))

  let offerersOptions = userOfferers.map((item) => ({
    value: item['id'].toString(),
    label: item['name'] as string,
  }))
  if (offerersOptions.length > 1) {
    offerersOptions = [
      { value: '', label: 'Selectionner une structure' },
      ...offerersOptions,
    ]
  }
  const { values, setValues } = useFormikContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section
      description="Le lieu de rattachement permet d’associer votre compte bancaire pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      {offerersOptions.length > 1 && (
        <FormLayout.Row>
          <Select
            onChange={(e) => onChangeOfferer(e.target.value)}
            disabled={offerersOptions.length === 1 || disableOfferSelection}
            label={OFFERER_LABEL}
            name="offererId"
            options={offerersOptions}
          />
        </FormLayout.Row>
      )}
      {isEligible === false && offerersOptions.length !== 0 && (
        <Callout
          links={[
            {
              href: 'https://www.demarches-simplifiees.fr/commencer/demande-de-referencement-sur-adage',
              label: 'Faire une demande de référencement',
              isExternal: true,
            },
            {
              href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
              label:
                'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
              isExternal: true,
            },
          ]}
          variant={CalloutVariant.WARNING}
        >
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez être référencé auprès du ministère de l’Éducation Nationale et
          du ministère de la Culture.
        </Callout>
      )}
      {offerersOptions.length === 0 && (
        <Banner>
          Vous ne pouvez pas créer d’offre collective tant que votre structure
          n’est pas validée.
        </Banner>
      )}
      {isEligible && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableVenueSelection}
            label={VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
            onChange={async (event) => {
              if (mode === Mode.CREATION) {
                await setValues(
                  applyVenueDefaultsToFormValues(
                    { ...values, venueId: event.target.value },
                    userOfferers,
                    isOfferCreated
                  )
                )
              }
            }}
          />
        </FormLayout.Row>
      )}
      {isEligible &&
        venuesOptions.length > 0 &&
        values.venueId.length === 0 &&
        values.offererId.length !== 0 && (
          <Callout
            links={[
              {
                href: `/structures/${values.offererId}/lieux/creation`,
                label: 'Renseigner un lieu',
              },
            ]}
            className={styles['banner-place-adress-info']}
            variant={CalloutVariant.ERROR}
          >
            Pour proposer des offres à destination d’un groupe scolaire, vous
            devez renseigner un lieu pour pouvoir être remboursé.
          </Callout>
        )}
    </FormLayout.Section>
  )
}

export default FormVenue
