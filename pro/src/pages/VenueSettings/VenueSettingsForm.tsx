import { useFormikContext } from 'formik'
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
import BankAccountInfos from 'pages/VenueCreation/BankAccountInfos/BankAccountInfos'
import { OffersSynchronization } from 'pages/VenueCreation/OffersSynchronization'
import { SiretOrCommentFields } from 'pages/VenueCreation/SiretOrCommentFields/SiretOrCommentFields'
import { VenueFormActionBar } from 'pages/VenueCreation/VenueFormActionBar/VenueFormActionBar'
import { WithdrawalDetails } from 'pages/VenueCreation/WithdrawalDetails'
import { TextInput, InfoBox, Select } from 'ui-kit'

import { VenueSettingsFormValues } from './types'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueLabels: SelectOption[]
  venueTypes: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsForm = ({
  offerer,
  updateIsSiretValued,
  venueLabels,
  venueTypes,
  provider,
  venueProvider,
  venue,
}: VenueFormProps) => {
  const { initialValues } = useFormikContext<VenueSettingsFormValues>()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()

  return (
    <>
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
            title="Adresse de l’activité"
            description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre activité. Elle ne sera affichée que si vous accueillez du public à cette adresse."
          >
            <FormLayout.Row>
              <AddressSelect />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

        <FormLayout.Section title="Activité principale">
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

          {!venue.isVirtual && (
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
          )}
        </FormLayout.Section>

        {!venue.isVirtual && <WithdrawalDetails />}

        <FormLayout.Section title="Notifications de réservations">
          <FormLayout.Row
            sideComponent={
              venue.isVirtual ? null : (
                <InfoBox>
                  Cette adresse s’appliquera par défaut à toutes vos offres,
                  vous pourrez la modifier à l’échelle de chaque offre.
                </InfoBox>
              )
            }
          >
            <TextInput
              name="bookingEmail"
              label="Adresse email"
              type="email"
              placeholder="email@exemple.com"
              isOptional={venue.isVirtual}
              disabled={venue.isVirtual}
            />
          </FormLayout.Row>
        </FormLayout.Section>

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

      <VenueFormActionBar venue={venue} />
    </>
  )
}
