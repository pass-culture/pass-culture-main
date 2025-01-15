import { useFormikContext } from 'formik'

import {
  CollectiveBookingStatus,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from 'commons/core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/form/Select/Select'

import { STRUCTURE_LABEL, VENUE_LABEL } from '../../constants/labels'

import styles from './FormVenue.module.scss'

interface FormVenueProps {
  userOfferer: GetEducationalOffererResponseModel | null
  venuesOptions: SelectOption[]
  isEligible: boolean | undefined
  disableForm: boolean
  isOfferCreated: boolean
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const FormVenue = ({
  userOfferer,
  venuesOptions,
  isEligible,
  disableForm,
  isOfferCreated,
  offer,
}: FormVenueProps): JSX.Element => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.lastBookingStatus
    : null
  const disableOfferSelection = disableForm || isOfferCreated
  const disabledBookingStatus = [
    CollectiveBookingStatus.USED,
    CollectiveBookingStatus.REIMBURSED,
  ]

  const disableVenueSelection =
    disableForm ||
    (lastBookingStatus !== undefined &&
      lastBookingStatus !== null &&
      disableOfferSelection &&
      disabledBookingStatus.includes(lastBookingStatus))

  const { values, setValues } = useFormikContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section title="Qui propose l’offre ?">
      {isEligible === false && userOfferer !== null && (
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
      {userOfferer === null && (
        <Callout
          variant={CalloutVariant.INFO}
          className={styles['no-offerer-callout']}
        >
          Vous ne pouvez pas créer d’offre collective tant que votre{' '}
          {isOfferAddressEnabled ? 'entité juridique' : 'structure'} n’est pas
          validée.
        </Callout>
      )}
      {isEligible && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableVenueSelection}
            label={isOfferAddressEnabled ? STRUCTURE_LABEL : VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
            onChange={async (event) => {
              if (!disableForm) {
                await setValues(
                  applyVenueDefaultsToFormValues(
                    { ...values, venueId: event.target.value },
                    userOfferer,
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
                href: isOfferAddressEnabled
                  ? '/parcours-inscription/structure'
                  : `/structures/${values.offererId}/lieux/creation`,
                label: `Renseigner ${isOfferAddressEnabled ? 'une structure' : 'un lieu'}`,
              },
            ]}
            className={styles['banner-place-adress-info']}
            variant={CalloutVariant.ERROR}
          >
            Pour proposer des offres à destination d’un groupe scolaire, vous
            devez renseigner{' '}
            {isOfferAddressEnabled ? 'une structure' : 'un lieu'} pour pouvoir
            être remboursé.
          </Callout>
        )}
    </FormLayout.Section>
  )
}
