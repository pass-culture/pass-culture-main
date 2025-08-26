import { useFormContext } from 'react-hook-form'

import { OfferStatus, type VenueListItemResponseModel } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { getIsOfferSubcategoryOnline } from '@/pages/IndividualOffer/commons/getIsOfferSubcategoryOnline'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import type { LocationFormValues } from '../../commons/types'
import styles from './LocationForm.module.scss'
import { PhysicalLocationSubform } from './PhysicalLocationSubform/PhysicalLocationSubform'

export interface LocationFormProps {
  offerVenue: VenueListItemResponseModel
}
export const LocationForm = ({ offerVenue }: LocationFormProps) => {
  const {
    register,
    formState: { errors },
  } = useFormContext<LocationFormValues>()

  const { hasPublishedOfferWithSameEan, offer, subCategories } =
    useIndividualOfferContext()
  assertOrFrontendError(offer, '`offer` is undefined in LocationForm.')

  const isOfferOnline = getIsOfferSubcategoryOnline(offer, subCategories)
  const mode = useOfferWizardMode()
  const isFormReadOnly =
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    hasPublishedOfferWithSameEan ||
    [OfferStatus.PENDING, OfferStatus.REJECTED].includes(offer.status) ||
    isOfferSynchronized(offer)

  return (
    <FormLayout.Section title="Où profiter de l’offre ?">
      <FormLayout.Row className={styles['row']}>
        {!isOfferOnline && (
          <PhysicalLocationSubform
            isDisabled={isFormReadOnly}
            venue={offerVenue}
          />
        )}

        {isOfferOnline && (
          <TextInput
            description="Format : https://exemple.com"
            disabled={isFormReadOnly}
            label="URL d’accès à l’offre"
            type="text"
            {...register('url')}
            error={errors.url?.message}
            required
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
