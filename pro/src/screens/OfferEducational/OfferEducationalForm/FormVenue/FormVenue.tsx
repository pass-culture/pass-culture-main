import { useFormikContext } from 'formik'
import React from 'react'

import {
  CollectiveBookingStatus,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import {
  applyVenueDefaultsToFormValues,
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  IOfferEducationalFormValues,
  isCollectiveOffer,
  Mode,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import { Banner, Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

interface FormVenueProps {
  userOfferers: GetEducationalOffererResponseModel[]
  venuesOptions: SelectOption[]
  isEligible: boolean | undefined
  mode: Mode
  isOfferCreated: boolean
  offer?: CollectiveOffer | CollectiveOfferTemplate
  categories: EducationalCategories
  onChangeOfferer: (event: string) => void
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  isEligible,
  mode,
  isOfferCreated,
  offer,
  categories,
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

  let offerersOptions = userOfferers.map(item => ({
    value: item['nonHumanizedId'].toString(),
    label: item['name'] as string,
  }))
  if (offerersOptions.length > 1) {
    offerersOptions = [
      { value: '', label: 'Selectionner une structure' },
      ...offerersOptions,
    ]
  }
  const { values, setValues } = useFormikContext<IOfferEducationalFormValues>()

  return (
    <FormLayout.Section
      description="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      <FormLayout.Row>
        <Select
          onChange={e => onChangeOfferer(e.target.value)}
          disabled={offerersOptions.length === 1 || disableOfferSelection}
          label={OFFERER_LABEL}
          name="offererId"
          options={offerersOptions}
        />
      </FormLayout.Row>
      {isEligible === false && offerersOptions.length !== 0 && (
        <Banner
          links={[
            {
              href: 'https://passculture.typeform.com/to/VtKospEg',
              linkTitle: 'Faire une demande de référencement',
            },
            {
              href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
              linkTitle:
                'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
            },
          ]}
        >
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez être référencé auprès du ministère de l’Éducation Nationale et
          du ministère de la Culture.
        </Banner>
      )}
      {offerersOptions.length === 0 && (
        <Banner>
          Vous ne pouvez pas créer d’offre collective tant que votre structure
          n’est pas validée.
        </Banner>
      )}
      {isEligible === true && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={
              venuesOptions.length === 1 || !isEligible || disableVenueSelection
            }
            label={VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
            onChange={event => {
              if (mode === Mode.CREATION) {
                setValues(
                  applyVenueDefaultsToFormValues(
                    { ...values, venueId: event.target.value },
                    userOfferers,
                    isOfferCreated,
                    categories
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
          <Banner
            links={[
              {
                href: `/structures/${values.offererId}/lieux/creation`,
                linkTitle: 'Renseigner un lieu',
              },
            ]}
          >
            Pour proposer des offres à destination d’un groupe scolaire, vous
            devez renseigner un lieu pour pouvoir être remboursé.
          </Banner>
        )}
    </FormLayout.Section>
  )
}

export default FormVenue
