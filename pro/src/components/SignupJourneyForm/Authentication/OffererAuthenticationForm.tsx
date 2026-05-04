import { useFormContext } from 'react-hook-form'

import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import type { Address } from '@/commons/context/SignupJourneyContext/types'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'

import styles from './OffererAuthenticationForm.module.scss'

export interface OffererAuthenticationFormValues extends Address {
  siret: string
  publicName?: string
  addressAutocomplete: string
  'search-addressAutocomplete': string
  coords?: string
  manuallySetAddress?: boolean
  isOpenToPublic?: string | undefined
}

export const OffererAuthenticationForm = (): JSX.Element => {
  const { offerer, initialAddress } = useSignupJourneyContext()
  const hasAllInitialAddressPart =
    initialAddress?.street && initialAddress?.postalCode && initialAddress?.city

  const isInitialAddress =
    initialAddress !== null &&
    initialAddress.addressAutocomplete ===
      `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`.trim()

  const {
    watch,
    setValue,
    register,
    clearErrors,
    formState: { errors, disabled },
  } = useFormContext<OffererAuthenticationFormValues>()

  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    resetReactHookFormAddressFields<OffererAuthenticationFormValues>(
      (name, defaultValue) => setValue(name, defaultValue)
    )
  }

  const shouldDisplayAddress =
    watch('isOpenToPublic') === undefined ||
    watch('isOpenToPublic') === 'true' ||
    !hasAllInitialAddressPart

  const notOpenToPublicLabel = hasAllInitialAddressPart
    ? 'Cette adresse postale ne sera pas visible.'
    : "Nous n'avons pas pu récupérer votre adresse automatiquement. Renseignez-en une pour continuer."

  return (
    <>
      <ScrollToFirstHookFormErrorAfterSubmit />
      <FormLayout.Section>
        <FormLayout.Row mdSpaceAfter>
          <TextInput
            {...register('publicName')}
            label="Nom public"
            required={!offerer?.isDiffusible}
            requiredIndicator="explicit"
            description="Ce nom sera affiché sur le pass Culture."
            error={errors.publicName?.message}
          />
        </FormLayout.Row>
        <FormLayout.Row
          mdSpaceAfter
          className={styles['open-to-public-toggle']}
        >
          <OpenToPublicToggle
            error={errors.isOpenToPublic?.message}
            onChange={(e) => {
              clearErrors('isOpenToPublic')

              if (e.target.value === 'true') {
                // The user is diffusible and had isOpenToPublic set to false. We reset it to the initial one
                if (offerer?.isDiffusible && !isInitialAddress) {
                  resetReactHookFormAddressFields((name, _) => {
                    // @ts-expect-error Type is right since it's gotten from the defaultValues
                    setValue(name, initialAddress[name])
                  })
                }

                // The user is not diffusible, we reset the fields to blank
                if (!offerer?.isDiffusible && hasAllInitialAddressPart) {
                  resetReactHookFormAddressFields<OffererAuthenticationFormValues>(
                    (name, defaultValue) => setValue(name, defaultValue)
                  )
                }
              } else if (
                (!isInitialAddress || !offerer?.isDiffusible) &&
                initialAddress &&
                hasAllInitialAddressPart
              ) {
                // We init the address fields as the default ones when the user untoggle the open to public toggle
                resetReactHookFormAddressFields((name, _) => {
                  // @ts-expect-error Type is right since it's gotten from the defaultValues
                  setValue(name, initialAddress[name])
                })
              }

              setValue('isOpenToPublic', e.target.value)
            }}
            isOpenToPublic={watch('isOpenToPublic')}
            overrideDescription="Sélectionnez une des options."
          />
        </FormLayout.Row>
        {shouldDisplayAddress && (
          <AddressFields
            addressRegister={register('addressAutocomplete')}
            disabled={disabled}
            onAddressChosen={(addressData) => {
              setValue('street', addressData.address)
              setValue('postalCode', addressData.postalCode)
              setValue('city', addressData.city)
              setValue('latitude', addressData.latitude)
              setValue('longitude', addressData.longitude)
              setValue('banId', addressData.id)
              setValue('inseeCode', addressData.inseeCode)
            }}
            onManualChange={toggleManuallySetAddress}
            renderManual={() => <AddressManual />}
            description={
              watch('isOpenToPublic') === 'false'
                ? notOpenToPublicLabel
                : 'Cette adresse postale sera affichée sur le pass Culture.'
            }
            error={errors.addressAutocomplete?.message}
            manual={manuallySetAddress}
            requiredIndicator="explicit"
          />
        )}
      </FormLayout.Section>
    </>
  )
}
