import { useFormikContext } from 'formik'
import React from 'react'

import { VenueProviderResponse } from 'apiClient/v1'
import ReimbursementFields from 'components/pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import { Address } from './Address'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { WithdrawalDetails } from './WithdrawalDetails'

import { IVenueFormValues } from '.'

interface IVenueForm {
  isCreatingVenue: boolean
  offerer: IOfferer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: IProviders[]
  venueProvider?: VenueProviderResponse[]
  venue?: IVenue
}

const VenueForm = ({
  isCreatingVenue,
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueLabels,
  provider,
  venueProvider,
  venue,
}: IVenueForm) => {
  const {
    isSubmitting,
    values: { isPermanent },
  } = useFormikContext<IVenueFormValues>()
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()

  return (
    <div>
      <FormLayout small>
        <FormLayout.MandatoryInfo />
        {!isCreatingVenue && provider && venueProvider && venue && (
          <OffersSynchronization
            provider={provider}
            venueProvider={venueProvider}
            venue={venue}
          />
        )}
        <Informations
          isCreatedEntity={isCreatingVenue}
          readOnly={!isCreatingVenue}
          updateIsSiretValued={updateIsSiretValued}
          venueIsVirtual={false}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && <ImageUploaderVenue />
        }
        <Address />
        <Activity venueTypes={venueTypes} venueLabels={venueLabels} />
        <Accessibility isCreatingVenue={isCreatingVenue} />
        <WithdrawalDetails isCreatedEntity={isCreatingVenue} />
        <Contact />
        <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
        {!isCreatingVenue && venue && (
          <ReimbursementFields
            offerer={offerer}
            readOnly={false}
            scrollToSection={false}
            venue={venue}
          />
        )}
        <SubmitButton isLoading={isSubmitting}>Valider</SubmitButton>
      </FormLayout>
    </div>
  )
}

export default VenueForm
