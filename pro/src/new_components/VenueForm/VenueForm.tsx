import { useFormikContext } from 'formik'
import React from 'react'

import ReimbursementFields from 'components/pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { IVenueProviderApi } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/CinemaProviderItem/types'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import { Accessibility } from './Accessibility'
import { Address } from './Address'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import styles from './VenueForm.module.scss'
import { WithdrawalDetails } from './WithdrawalDetails'

import { IVenueFormValues } from '.'

interface IVenueForm {
  isCreatingVenue: boolean
  offerer: IOfferer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: IProviders[]
  venueProvider?: IVenueProviderApi[]
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
      <FormLayout className={styles['venue-form']} small>
        <p className={styles['venue-form-description']}>
          Tous les champs sont obligatoires sauf mention contraire.
        </p>
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
          venueTypes={venueTypes}
          venueLabels={venueLabels}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && <ImageUploaderVenue />
        }
        <Address />
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
