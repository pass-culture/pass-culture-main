import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { Select, TextArea } from 'ui-kit'

import { Accessibility } from './Accessibility'
import BankAccountInfos from './BankAccountInfos/BankAccountInfos'
import { Contact } from './Contact'
import { VenueFormActionBar } from './VenueFormActionBar'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  venueLabels: SelectOption[]
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({
  offerer,
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

        {!venue.isVirtual && (
          <FormLayout.Section
            title="À propos de votre activité"
            description={
              venue.isVirtual
                ? undefined
                : 'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
            }
          >
            <FormLayout.Row>
              <TextArea
                name="description"
                label="Description"
                placeholder="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                maxLength={1000}
                countCharacters
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <Select
                options={[
                  {
                    value: '',
                    label:
                      'Si votre lieu est labellisé précisez-le en le sélectionnant',
                  },
                  ...venueLabels,
                ]}
                name="venueLabel"
                label="Label du ministère de la Culture ou du Centre national du cinéma et de l’image animée"
                isOptional
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

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
