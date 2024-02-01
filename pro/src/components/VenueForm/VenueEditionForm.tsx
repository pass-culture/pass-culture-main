import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { VenueProviderResponse } from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { Offerer } from 'core/Offerers/types'
import { Providers, Venue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import BankAccountInfos from './BankAccountInfos/BankAccountInfos'
import CollectiveVenueInformations from './CollectiveVenueInformations/CollectiveVenueInformations'
import { Contact } from './Contact'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

import { VenueFormValues } from '.'

interface VenueFormProps {
  offerer: Offerer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue: Venue
  initialIsVirtual?: boolean
}

export const VenueEditionForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueLabels,
  provider,
  venueProvider,
  venue,
  initialIsVirtual = false,
}: VenueFormProps) => {
  const {
    values: { isPermanent },
  } = useFormikContext<VenueFormValues>()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()

  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)

  useEffect(() => {
    const loadCanOffererCreateCollectiveOffer = async () => {
      const response = await canOffererCreateCollectiveOfferAdapter(offerer.id)
      setCanOffererCreateCollectiveOffer(
        response.payload.isOffererEligibleToEducationalOffer
      )
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadCanOffererCreateCollectiveOffer()
  }, [offerer.id])

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        {!initialIsVirtual && provider && venueProvider && (
          <OffersSynchronization
            provider={provider}
            venueProvider={venueProvider}
            venue={venue}
          />
        )}

        <Informations
          isCreatedEntity={false}
          readOnly={true}
          updateIsSiretValued={updateIsSiretValued}
          isVenueVirtual={initialIsVirtual}
          siren={offerer.siren}
        />

        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && (
            <ImageUploaderVenue isCreatingVenue={false} />
          )
        }

        {!initialIsVirtual && (
          <FormLayout.Section
            title="Adresse du lieu"
            description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
          >
            <FormLayout.Row>
              <AddressSelect />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

        <Activity
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={false}
        />

        {!initialIsVirtual && (
          <>
            <Accessibility isCreatingVenue={false} />
            <WithdrawalDetails />
          </>
        )}

        <Contact isVenueVirtual={initialIsVirtual} isCreatingVenue={false} />

        {(canOffererCreateCollectiveOffer ||
          Boolean(venue?.collectiveDmsApplication)) && (
          <CollectiveVenueInformations
            venue={venue}
            isCreatingVenue={false}
            canCreateCollectiveOffer={canOffererCreateCollectiveOffer}
          />
        )}

        {(!isNewBankDetailsJourneyEnabled ||
          (isNewBankDetailsJourneyEnabled && !venue?.siret)) && (
          <ReimbursementFields
            offerer={offerer}
            scrollToSection={Boolean(location.state) || Boolean(location.hash)}
            venue={venue}
          />
        )}

        {isNewBankDetailsJourneyEnabled && (
          <BankAccountInfos venueBankAccount={venue.bankAccount} />
        )}

        <VenueFormActionBar offererId={offerer.id} isCreatingVenue={false} />
      </FormLayout>
    </div>
  )
}
