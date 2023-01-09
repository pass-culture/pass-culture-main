import { useFormikContext } from 'formik'
import React from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import {
  applyVenueDefaultsToFormValues,
  IOfferEducationalFormValues,
  Mode,
} from 'core/OfferEducational'
import { Banner, Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

interface IFormVenueProps {
  userOfferers: GetEducationalOffererResponseModel[]
  venuesOptions: SelectOptions
  isEligible: boolean | undefined
  mode: Mode
  isOfferCreated: boolean
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  isEligible,
  mode,
  isOfferCreated,
}: IFormVenueProps): JSX.Element => {
  const disableForm = mode !== Mode.CREATION || isOfferCreated

  let offerersOptions = userOfferers.map(item => ({
    value: item['id'] as string,
    label: item['name'] as string,
  }))
  if (offerersOptions.length > 1) {
    offerersOptions = [
      { value: '', label: 'Selectionner une structure' },
      ...offerersOptions,
    ]
  }

  const { values, setFieldValue, setValues } =
    useFormikContext<IOfferEducationalFormValues>()

  return (
    <FormLayout.Section
      description="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      <FormLayout.Row>
        <Select
          onChange={() => setFieldValue('venueId', '')}
          disabled={offerersOptions.length === 1 || disableForm}
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
            disabled={venuesOptions.length === 1 || !isEligible || disableForm}
            label={VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
            onChange={event => {
              if (mode === Mode.CREATION) {
                setValues(
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
