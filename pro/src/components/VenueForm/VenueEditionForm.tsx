import { useLocation } from 'react-router-dom'

import {
  GetOffererResponseModel,
  VenueProviderResponse,
  GetVenueResponseModel,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import BankAccountInfos from './BankAccountInfos/BankAccountInfos'
import { Contact } from './Contact'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({
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
