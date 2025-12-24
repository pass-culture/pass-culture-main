import { useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { AdresseData } from '@/apiClient/adresse/types'
import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { ReimbursementFields } from '@/pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { VenueFormActionBar } from '@/pages/VenueEdition/components/VenueFormActionBar/VenueFormActionBar'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from '@/ui-kit/form/AddressSelect/AddressSelect'
import { Select } from '@/ui-kit/form/Select/Select'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../commons/types'
import { SiretOrCommentFields } from './SiretOrCommentFields/SiretOrCommentFields'
import { OffersSynchronization } from './VenueProvidersManager/OffersSynchronization/OffersSynchronization'
import { WithdrawalDetails } from './WithdrawalDetails/WithdrawalDetails'

export interface VenueSettingsFormProps {
  offerer: GetOffererResponseModel
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
  formContext: VenueSettingsFormContext
}

export const VenueSettingsForm = ({
  offerer,
  venueTypes,
  venueProviders,
  venue,
  formContext,
}: VenueSettingsFormProps) => {
  const {
    register,
    setValue,
    watch,
    clearErrors,
    formState: { isDirty, isSubmitting, isSubmitted, errors },
  } = useFormContext<VenueSettingsFormValues>()

  const isVenueActivityFeatureActive = useActiveFeature('WIP_VENUE_ACTIVITY')

  const location = useLocation()
  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    resetReactHookFormAddressFields((name, defaultValue) =>
      setValue(name, defaultValue)
    )
    clearErrors()
  }

  const onAddressSelect = (data: AdresseData) => {
    setValue('street', data.address)
    setValue('postalCode', data.postalCode)
    setValue('city', data.city)
    setValue('latitude', data.latitude.toString())
    setValue('longitude', data.longitude.toString())
    setValue('banId', data.id)
    setValue('inseeCode', data.inseeCode)
    setValue('coords', `${data.latitude}, ${data.longitude}`)
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
              <SiretOrCommentFields formContext={formContext} />
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
              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  {...register('publicName')}
                  label="Nom public"
                  description="À remplir si différent de la raison sociale. En le
                    remplissant, c’est ce dernier qui sera visible du public."
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <AddressSelect
                  {...register('addressAutocomplete')}
                  disabled={manuallySetAddress}
                  label={'Adresse postale'}
                  onAddressChosen={onAddressSelect}
                  error={errors.addressAutocomplete?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <Button
                  variant={ButtonVariant.QUATERNARY}
                  icon={manuallySetAddress ? fullBackIcon : fullNextIcon}
                  onClick={toggleManuallySetAddress}
                >
                  {manuallySetAddress
                    ? 'Revenir à la sélection automatique'
                    : 'Vous ne trouvez pas votre adresse ?'}
                </Button>
              </FormLayout.Row>
              {manuallySetAddress && <AddressManual />}
            </>
          )}
        </FormLayout.Section>

        {!isVenueActivityFeatureActive && (
          <FormLayout.Section title="Activité principale">
            <FormLayout.Row>
              <Select
                {...register('venueType')}
                options={venueTypes}
                label="Activité principale"
                disabled={venue.isVirtual}
                error={errors.venueType?.message}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

        {!venue.isVirtual && <WithdrawalDetails />}

        <FormLayout.Section title="Notifications de réservations">
          <FormLayout.Row
            sideComponent={
              venue.isVirtual ? null : (
                <TipsBanner>
                  Cette adresse s’appliquera par défaut à toutes vos offres,
                  vous pourrez la modifier à l’échelle de chaque offre.
                </TipsBanner>
              )
            }
          >
            <TextInput
              {...register('bookingEmail')}
              label="Adresse email"
              type="email"
              description="Format : email@exemple.com"
              required={!venue.isVirtual}
              disabled={venue.isVirtual}
              error={errors.bookingEmail?.message}
            />
          </FormLayout.Row>
        </FormLayout.Section>

        <ReimbursementFields
          offerer={offerer}
          scrollToSection={Boolean(location.state) || Boolean(location.hash)}
          venue={venue}
        />
      </FormLayout>
      <VenueFormActionBar venue={venue} isSubmitting={isSubmitting} />
      <RouteLeavingGuardIndividualOffer
        when={isDirty && !isSubmitting && !isSubmitted}
      />
    </>
  )
}
