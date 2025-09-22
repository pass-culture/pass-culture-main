import { useFormContext } from 'react-hook-form'

import { OfferStatus, type VenueListItemResponseModel } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'

import type { LocationFormValues } from '../../commons/types'
import { PhysicalLocationSubform } from './PhysicalLocationSubform/PhysicalLocationSubform'

interface LocationFormProps {
  offerVenue: VenueListItemResponseModel
}
export const LocationForm = ({ offerVenue }: LocationFormProps) => {
  const {
    register,
    formState: { errors },
  } = useFormContext<LocationFormValues>()

  const { hasPublishedOfferWithSameEan, offer } = useIndividualOfferContext()
  assertOrFrontendError(offer, '`offer` is undefined in LocationForm.')

  const mode = useOfferWizardMode()
  const isFormReadOnly =
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    hasPublishedOfferWithSameEan ||
    [OfferStatus.PENDING, OfferStatus.REJECTED].includes(offer.status) ||
    isOfferSynchronized(offer)

  return (
    <FormLayout.Section title="Où profiter de l’offre ?">
      <FormLayout.Row>
        {!offer.isDigital && (
          <PhysicalLocationSubform
            isDisabled={isFormReadOnly}
            venue={offerVenue}
          />
        )}

        {offer.isDigital && (
          <TextInput
            description="Format : https://exemple.com"
            disabled={isFormReadOnly}
            label="URL d’accès à l’offre"
            type="url"
            {...register('url')}
            error={errors.url?.message}
            required
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
