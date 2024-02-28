import { useLocation } from 'react-router-dom'

import {
  GetOffererResponseModel,
  VenueProviderResponse,
  GetVenueResponseModel,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import { Activity } from 'components/VenueForm//Activity'
import BankAccountInfos from 'components/VenueForm//BankAccountInfos/BankAccountInfos'
import { Contact } from 'components/VenueForm//Contact'
import { Informations } from 'components/VenueForm//Informations'
import { OffersSynchronization } from 'components/VenueForm//OffersSynchronization'
import { VenueFormActionBar } from 'components/VenueForm//VenueFormActionBar'
import { WithdrawalDetails } from 'components/VenueForm//WithdrawalDetails'
import { Accessibility } from 'components/VenueForm/Accessibility'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueLabels,
  provider,
  venueProvider,
  venue,
}: VenueFormProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        {!venue.isVirtual && provider && venueProvider && (
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
          isVenueVirtual={venue.isVirtual}
          siren={offerer.siren}
        />

        {!venue.isVirtual && (
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
          isVenueVirtual={venue.isVirtual}
          isCreatingVenue={false}
        />

        {!venue.isVirtual && (
          <>
            <Accessibility isCreatingVenue={false} />
            <WithdrawalDetails />
          </>
        )}

        <Contact isVenueVirtual={venue.isVirtual} isCreatingVenue={false} />

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

        <VenueFormActionBar isCreatingVenue={false} />
      </FormLayout>
    </div>
  )
}
