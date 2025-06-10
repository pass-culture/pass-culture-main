import { useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'

import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { AddressFormValues } from 'commons/core/shared/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ReimbursementFields } from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { buildVenueTypesOptions } from 'pages/VenueEdition/buildVenueTypesOptions'
import { VenueFormActionBar } from 'pages/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/formV2/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/formV2/AddressSelect/AddressSelect'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
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

const fieldsNames: Map<keyof AddressFormValues, string | null> = new Map([
  ['street', ''],
  ['postalCode', ''],
  ['city', ''],
  ['latitude', ''],
  ['longitude', ''],
  ['coords', ''],
  ['banId', ''], // TODO: See with backend if it's preferable to send also "null" to be consistent with "inseeCode"
  ['inseeCode', null],
  ['search-addressAutocomplete', ''],
  ['addressAutocomplete', ''],
])

export const VenueSettingsForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueProviders,
  venue,
}: VenueFormProps) => {
  const methods = useFormContext<VenueSettingsFormValues>()
  const {
    getValues,
    register,
    setValue,
    watch,
    clearErrors,
    formState: { isDirty, isSubmitting, errors },
  } = methods

  const location = useLocation()
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)
  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    return [...fieldsNames.entries()].map(([fieldName, defaultValue]) => {
      setValue(fieldName as keyof VenueSettingsFormValues, defaultValue)
      clearErrors()
    })
  }

  return (
    <>
      <ScrollToFirstHookFormErrorAfterSubmit />

      {!venue.isVirtual && (
        <OffersSynchronization venueProviders={venueProviders} venue={venue} />
      )}

      <FormLayout fullWidthActions>
        <FormLayout.Section title="Informations administratives">
          {!venue.isVirtual && (
            <FormLayout.Row>
              <SiretOrCommentFields
                initialSiret={getValues('siret')}
                isToggleDisabled
                isCreatedEntity={false}
                updateIsSiretValued={updateIsSiretValued}
                siren={offerer.siren}
              />
            </FormLayout.Row>
          )}

          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Raison sociale"
              {...register('name')}
              disabled
              error={errors.name?.message}
            />
          </FormLayout.Row>

          {!venue.isVirtual && (
            <>
              <FormLayout.Row
                mdSpaceAfter
                sideComponent={
                  <InfoBox>
                    À remplir si différent de la raison sociale. En le
                    remplissant, c’est ce dernier qui sera visible du public.
                  </InfoBox>
                }
              >
                <TextInput {...register('publicName')} label="Nom public" />
              </FormLayout.Row>

              <FormLayout.Row>
                <AddressSelect
                  {...register('addressAutocomplete')}
                  disabled={manuallySetAddress}
                  label={'Adresse postale'}
                  onAddressChosen={(addressData) => {
                    setValue('manuallySetAddress', false)
                    setValue('street', addressData.address)
                    setValue('postalCode', addressData.postalCode)
                    setValue('city', addressData.city)
                    setValue('latitude', String(addressData.latitude))
                    setValue('longitude', String(addressData.longitude))
                    setValue('banId', addressData.id)
                    setValue('inseeCode', addressData.inseeCode)
                  }}
                  error={errors.addressAutocomplete?.message}
                />
              </FormLayout.Row>

              <>
                <FormLayout.Row>
                  <Button
                    variant={ButtonVariant.QUATERNARY}
                    icon={manuallySetAddress ? fullBackIcon : fullNextIcon}
                    onClick={toggleManuallySetAddress}
                  >
                    {manuallySetAddress ? (
                      <>Revenir à la sélection automatique</>
                    ) : (
                      <>Vous ne trouvez pas votre adresse ?</>
                    )}
                  </Button>
                </FormLayout.Row>
                {manuallySetAddress && <AddressManual />}
              </>
            </>
          )}
        </FormLayout.Section>

        <FormLayout.Section title="Activité principale">
          <FormLayout.Row>
            <Select
              {...register('venueType')}
              options={[
                {
                  value: '',
                  label: 'Sélectionnez celui qui correspond à votre lieu',
                },
                ...venueTypesOptions,
              ]}
              label="Activité principale"
              disabled={venue.isVirtual}
              error={errors.venueType?.message}
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
              {...register('bookingEmail')}
              name="bookingEmail"
              label="Adresse email"
              type="email"
              description="Format : email@exemple.com"
              required={!venue.isVirtual}
              disabled={venue.isVirtual}
              error={errors.bookingEmail?.message}
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

      <VenueFormActionBar venue={venue} isSubmitting={isSubmitting} />
      <RouteLeavingGuardIndividualOffer when={isDirty && !isSubmitting} />
    </>
  )
}
