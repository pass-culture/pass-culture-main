import { useFormContext } from 'react-hook-form'

import {
  CollectiveBookingStatus,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  isCollectiveOffer,
  OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { applyVenueDefaultsToFormValues } from '@/commons/core/OfferEducational/utils/applyVenueDefaultsToFormValues'
import { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Select } from '@/ui-kit/form/Select/Select'

import { STRUCTURE_LABEL } from '../../constants/labels'

interface FormVenueProps {
  userOfferer: GetEducationalOffererResponseModel | null
  venuesOptions: SelectOption[]
  isEligible: boolean | undefined
  disableForm: boolean
  isOfferCreated: boolean
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  venues?: VenueListItemResponseModel[]
}

export const FormVenue = ({
  userOfferer,
  venuesOptions,
  isEligible,
  disableForm,
  isOfferCreated,
  offer,
  venues,
}: FormVenueProps): JSX.Element => {
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.booking?.status
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

  const { watch, setValue, register, formState } =
    useFormContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section title="Qui propose l’offre ?">
      {isEligible && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableVenueSelection}
            label={STRUCTURE_LABEL}
            {...register('venueId')}
            options={venuesOptions}
            required
            error={formState.errors.venueId?.message}
            onChange={(event) => {
              if (!disableForm) {
                Object.entries(
                  applyVenueDefaultsToFormValues(
                    { ...watch(), venueId: event.target.value },
                    userOfferer,
                    isOfferCreated,
                    venues
                  )
                ).map(([key, val]) => {
                  setValue(key as keyof OfferEducationalFormValues, val)
                })
              }
            }}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}
