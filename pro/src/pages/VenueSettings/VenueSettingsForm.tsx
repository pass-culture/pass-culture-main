import { useFormikContext } from 'formik'
import { useLocation } from 'react-router-dom'

import {
  GetOffererResponseModel,
  VenueProviderResponse,
  GetVenueResponseModel,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import { VenueFormValues } from 'components/VenueForm'
import BankAccountInfos from 'components/VenueForm//BankAccountInfos/BankAccountInfos'
import { Contact } from 'components/VenueForm//Contact'
import { OffersSynchronization } from 'components/VenueForm//OffersSynchronization'
import { VenueFormActionBar } from 'components/VenueForm//VenueFormActionBar'
import { WithdrawalDetails } from 'components/VenueForm//WithdrawalDetails'
import SiretOrCommentFields from 'components/VenueForm/Informations/SiretOrCommentFields'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { TextInput, InfoBox, Select } from 'ui-kit'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  provider,
  venueProvider,
  venue,
}: VenueFormProps) => {
  const { initialValues } = useFormikContext<VenueFormValues>()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()

  return (
    <div>
      <FormLayout fullWidthActions>
        {!venue.isVirtual && provider && venueProvider && (
          <OffersSynchronization
            provider={provider}
            venueProvider={venueProvider}
            venue={venue}
          />
        )}

        <FormLayout.Section title="Informations administratives">
          {!venue.isVirtual && (
            <FormLayout.Row>
              <SiretOrCommentFields
                initialSiret={initialValues.siret}
                readOnly
                isToggleDisabled
                isCreatedEntity={false}
                updateIsSiretValued={updateIsSiretValued}
                siren={offerer.siren}
              />
            </FormLayout.Row>
          )}

          <FormLayout.Row>
            <TextInput name="name" label="Raison sociale" disabled />
          </FormLayout.Row>

          {!venue.isVirtual && (
            <FormLayout.Row
              sideComponent={
                <InfoBox>
                  À remplir si différent de la raison sociale. En le
                  remplissant, c’est ce dernier qui sera visible du public.
                </InfoBox>
              }
            >
              <TextInput name="publicName" label="Nom public" isOptional />
            </FormLayout.Row>
          )}
        </FormLayout.Section>

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

        <FormLayout.Section
          title="Activité principale"
          description={
            venue.isVirtual
              ? undefined
              : 'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
          }
        >
          <FormLayout.Row>
            <Select
              options={[
                {
                  value: '',
                  label: 'Sélectionnez celui qui correspond à votre lieu',
                },
                ...venueTypes,
              ]}
              name="venueType"
              label="Activité principale"
              disabled={venue.isVirtual}
            />
          </FormLayout.Row>
        </FormLayout.Section>

        {!venue.isVirtual && <WithdrawalDetails />}

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
