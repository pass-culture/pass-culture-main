import { useField, useFormikContext } from 'formik'
import { useLocation } from 'react-router'

import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { resetAddressFields } from 'commons/utils/resetAddressFields'
import { AddressSelect } from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ReimbursementFields } from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { buildVenueTypesOptions } from 'pages/VenueEdition/buildVenueTypesOptions'
import { VenueFormActionBar } from 'pages/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { SiretOrCommentFields } from './SiretOrCommentFields/SiretOrCommentFields'
import { VenueSettingsFormValues } from './types'
import { OffersSynchronization } from './VenueProvidersManager/OffersSynchronization/OffersSynchronization'
import { WithdrawalDetails } from './WithdrawalDetails/WithdrawalDetails'

interface VenueFormProps {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueProviders,
  venue,
}: VenueFormProps) => {
  const formik = useFormikContext<VenueSettingsFormValues>()
  const { initialValues, dirty, isSubmitting } = formik
  const location = useLocation()
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)

  const [manuallySetAddress, , { setValue: setManuallySetAddress }] =
    useField('manuallySetAddress')

  const toggleManuallySetAddress = async () => {
    const isAddressManual = !manuallySetAddress.value
    await setManuallySetAddress(isAddressManual)
    if (isAddressManual) {
      await resetAddressFields({ formik })
    }
  }

  return (
    <>
      <ScrollToFirstErrorAfterSubmit />

      {!venue.isVirtual && (
        <OffersSynchronization venueProviders={venueProviders} venue={venue} />
      )}

      <FormLayout fullWidthActions>
        <FormLayout.Section title="Informations administratives">
          {!venue.isVirtual && (
            <FormLayout.Row>
              <SiretOrCommentFields
                initialSiret={initialValues.siret}
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
            <>
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

              <FormLayout.Row>
                <AddressSelect disabled={manuallySetAddress.value} />
              </FormLayout.Row>

              <>
                <FormLayout.Row>
                  <Button
                    variant={ButtonVariant.QUATERNARY}
                    icon={
                      manuallySetAddress.value ? fullBackIcon : fullNextIcon
                    }
                    onClick={toggleManuallySetAddress}
                  >
                    {manuallySetAddress.value ? (
                      <>Revenir à la sélection automatique</>
                    ) : (
                      <>Vous ne trouvez pas votre adresse ?</>
                    )}
                  </Button>
                </FormLayout.Row>
                {manuallySetAddress.value && <AddressManual />}
              </>
            </>
          )}
        </FormLayout.Section>

        <FormLayout.Section title="Activité principale">
          <FormLayout.Row>
            <Select
              options={[
                {
                  value: '',
                  label: 'Sélectionnez celui qui correspond à votre lieu',
                },
                ...venueTypesOptions,
              ]}
              name="venueType"
              label="Activité principale"
              disabled={venue.isVirtual}
            />
          </FormLayout.Row>
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
              description="Format : email@exemple.com"
              isOptional={venue.isVirtual}
              disabled={venue.isVirtual}
            />
          </FormLayout.Row>
        </FormLayout.Section>

        {!venue.siret && (
          <ReimbursementFields
            offerer={offerer}
            scrollToSection={Boolean(location.state) || Boolean(location.hash)}
            venue={venue}
          />
        )}
      </FormLayout>

      <VenueFormActionBar venue={venue} disableFormSubmission={!formik.dirty} />
      <RouteLeavingGuardIndividualOffer when={dirty && !isSubmitting} />
    </>
  )
}
