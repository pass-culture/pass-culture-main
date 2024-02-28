import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import BankAccountInfos from './BankAccountInfos/BankAccountInfos'
import { Contact } from './Contact'
import { VenueFormActionBar } from './VenueFormActionBar'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({
  offerer,
  venueTypes,
  venueLabels,
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

        <Activity
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          isVenueVirtual={venue.isVirtual}
          isCreatingVenue={false}
        />

        {!venue.isVirtual && <Accessibility isCreatingVenue={false} />}

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
      </FormLayout>
      <VenueFormActionBar isCreatingVenue={false} />
    </div>
  )
}
