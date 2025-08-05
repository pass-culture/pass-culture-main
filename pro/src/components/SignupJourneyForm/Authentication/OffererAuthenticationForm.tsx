import { Address } from 'commons/core/shared/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { resetReactHookFormAddressFields } from 'commons/utils/resetAddressFields'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OpenToPublicToggle } from 'components/OpenToPublicToggle/OpenToPublicToggle'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { useFormContext } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/form/AddressSelect/AddressSelect'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { OffererFormValues } from '../Offerer/Offerer'

import styles from './OffererAuthenticationForm.module.scss'

export interface OffererAuthenticationFormValues
  extends OffererFormValues,
    Address {
  name: string
  publicName: string
  addressAutocomplete: string
  'search-addressAutocomplete': string
  coords?: string
  manuallySetAddress?: boolean
  isOpenToPublic?: string
}

export const OffererAuthenticationForm = (): JSX.Element => {
  const isPartiallyDiffusableSignupEnabled = useActiveFeature(
    'WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE'
  )

  const { watch, setValue, register, getFieldState } =
    useFormContext<OffererAuthenticationFormValues>()

  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    resetReactHookFormAddressFields((name, defaultValue) =>
      setValue(name, defaultValue)
    )
  }

  // TODO: change this condition in the right jira story
  const shouldDisplayAddress =
    !isPartiallyDiffusableSignupEnabled || watch('isOpenToPublic') === 'true'

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
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          {...register('name')}
          label="Raison sociale"
          type="text"
          required={true}
          disabled
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          {...register('publicName')}
          label="Nom public"
          type="text"
          description="À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public."
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <OpenToPublicToggle
          className={styles['open-to-public-toggle']}
          onChange={(e) => {
            setValue('isOpenToPublic', e.target.value)
          }}
          isOpenToPublic={watch('isOpenToPublic')}
          showDescription={false}
        />
      </FormLayout.Row>
      {shouldDisplayAddress && (
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
          {manuallySetAddress && <AddressManual />}
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}
