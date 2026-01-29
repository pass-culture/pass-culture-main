import { useFormContext } from 'react-hook-form'

import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import type { Address } from '@/commons/core/shared/types'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from '@/ui-kit/form/AddressSelect/AddressSelect'

import styles from './OffererAuthenticationForm.module.scss'

export interface OffererAuthenticationFormValues extends Address {
  siret: string
  name: string
  publicName?: string
  addressAutocomplete: string
  'search-addressAutocomplete': string
  coords?: string
  manuallySetAddress?: boolean
  isOpenToPublic?: string | undefined
}

export const OffererAuthenticationForm = (): JSX.Element => {
  const { offerer, initialAddress } = useSignupJourneyContext()

  const {
    watch,
    setValue,
    register,
    getFieldState,
    clearErrors,
    formState: { errors },
  } = useFormContext<OffererAuthenticationFormValues>()

  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    resetReactHookFormAddressFields<OffererAuthenticationFormValues>(
      (name, defaultValue) => setValue(name, defaultValue)
    )
  }

  const shouldDisplayAddress =
    watch('isOpenToPublic') === 'true' || offerer?.isDiffusible

  return (
    <FormLayout.Section>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          {...register('siret')}
          label="Numéro de SIRET"
          type="text"
          required={true}
          disabled
        />
      </FormLayout.Row>
      {offerer?.isDiffusible ? (
        <FormLayout.Row mdSpaceAfter>
          <TextInput
            {...register('name')}
            label="Raison sociale"
            type="text"
            required
            disabled
          />
        </FormLayout.Row>
      ) : (
        <FormLayout.Row mdSpaceAfter className={styles['disabled-row']}>
          <TextInput
            value={offerer?.postalCode}
            name="initial-postalCode"
            label="Code postal"
            disabled
          />
          <TextInput
            name="initial-city"
            label="Ville"
            disabled
            value={offerer?.city}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          {...register('publicName')}
          label="Nom public"
          required={!offerer?.isDiffusible}
          description={
            offerer?.isDiffusible
              ? 'À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public.'
              : ''
          }
          error={errors.publicName?.message}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter className={styles['open-to-public-toggle']}>
        <OpenToPublicToggle
          error={errors.isOpenToPublic?.message}
          onChange={(e) => {
            clearErrors('isOpenToPublic')
            if (!offerer?.isDiffusible) {
              if (e.target.value === 'true') {
                // We reset the address fields when the user toggles the open to public toggle when they aren't diffusible
                resetReactHookFormAddressFields<OffererAuthenticationFormValues>(
                  (name, defaultValue) => setValue(name, defaultValue)
                )
              } else {
                // We init the address fields as the default ones when the user untoggle the open to public toggle when they are not diffusible
                if (initialAddress) {
                  resetReactHookFormAddressFields((name, _) => {
                    // @ts-expect-error Type is right since it's gotten from the defaultValues
                    setValue(name, initialAddress[name])
                  })
                }
              }
            }
            setValue('isOpenToPublic', e.target.value)
          }}
          isOpenToPublic={watch('isOpenToPublic')}
          overrideDescription="Sélectionnez une des options."
        />
      </FormLayout.Row>
      {shouldDisplayAddress && (
        <>
          <FormLayout.Row>
            <AddressSelect
              {...register('addressAutocomplete')}
              label={'Adresse postale'}
              description={
                watch('isOpenToPublic') === 'true'
                  ? 'Cette adresse postale sera visible.'
                  : 'Cette adresse postale ne sera pas visible.'
              }
              disabled={manuallySetAddress}
              error={getFieldState('addressAutocomplete').error?.message}
              onAddressChosen={(addressData) => {
                setValue('street', addressData.address)
                setValue('postalCode', addressData.postalCode)
                setValue('city', addressData.city)
                setValue('latitude', addressData.latitude)
                setValue('longitude', addressData.longitude)
                setValue('banId', addressData.id)
                setValue('inseeCode', addressData.inseeCode)
              }}
            />
          </FormLayout.Row>
          <FormLayout.Row className={styles['manual-address-button']}>
            <Button
              type="button"
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={manuallySetAddress ? fullBackIcon : fullNextIcon}
              onClick={toggleManuallySetAddress}
              label={
                manuallySetAddress
                  ? 'Revenir à la sélection automatique'
                  : 'Vous ne trouvez pas votre adresse ?'
              }
            />
            {manuallySetAddress && <AddressManual />}
          </FormLayout.Row>
        </>
      )}
    </FormLayout.Section>
  )
}
