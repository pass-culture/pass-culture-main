import cn from 'classnames'
import { useFormContext } from 'react-hook-form'

import { AddressFormValues } from 'commons/core/shared/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { Address } from 'components/Address/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OpenToPublicToggle } from 'components/OpenToPublicToggle/OpenToPublicToggle'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/formV2/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/formV2/AddressSelect/AddressSelect'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { OffererFormValues } from '../Offerer/Offerer'

import styles from './OffererAuthenticationForm.module.scss'

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
  const { watch, setValue, register, getFieldState, resetField } =
    useFormContext<OffererAuthenticationFormValues>()

  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')
  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)

    return [...fieldsNames.entries()].map(([fieldName, defaultValue]) => {
      resetField(fieldName as keyof OffererAuthenticationFormValues, {
        defaultValue: defaultValue,
      })
    })
  }

  return (
    <FormLayout.Section>
      <h1 className={styles['title']}>Identification</h1>
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
        <AddressSelect
          {...register('addressAutocomplete')}
          label={'Adresse postale'}
          description="À modifier si l’adresse postale de votre structure est différente de la raison sociale."
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
      <FormLayout.Row>
        {isOpenToPublicEnabled && (
          <OpenToPublicToggle
            className={cn(styles['open-to-public-toggle'], {
              [styles['open-to-public-toggle-address-manual-open']]:
                manuallySetAddress,
            })}
            onChange={(e) => {
              setValue('isOpenToPublic', e.target.value)
            }}
            isOpenToPublic={watch('isOpenToPublic')}
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
