import { useField, useFormikContext } from 'formik'

import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { resetAddressFields } from 'commons/utils/resetAddressFields'
import { AddressSelect } from 'components/Address/Address'
import { Address } from 'components/Address/types'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OpenToPublicToggle } from 'components/OpenToPublicToggle/OpenToPublicToggle'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
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
  const formik = useFormikContext<OffererAuthenticationFormValues>()
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')

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
    <FormLayout.Section>
      <h1 className={styles['title']}>Identification</h1>
      <FormLayout.Row>
        <TextInput name="siret" label="Numéro de SIRET" type="text" disabled />
        <TextInput name="name" label="Raison sociale" type="text" disabled />
        <TextInput
          name="publicName"
          label="Nom public"
          type="text"
          isOptional
          description="À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public."
        />
        <AddressSelect
          description="À modifier si l’adresse postale de votre structure est différente de la raison sociale."
          disabled={manuallySetAddress.value}
        />
        <Button
          variant={ButtonVariant.QUATERNARY}
          icon={manuallySetAddress.value ? fullBackIcon : fullNextIcon}
          onClick={toggleManuallySetAddress}
        >
          {manuallySetAddress.value ? (
            <>Revenir à la sélection automatique</>
          ) : (
            <>Vous ne trouvez pas votre adresse ?</>
          )}
        </Button>
        {manuallySetAddress.value && <AddressManual />}
        {isOpenToPublicEnabled && (
          <OpenToPublicToggle
            onChange={async (e) => {
              await formik.setFieldValue('isOpenToPublic', e.target.value)
            }}
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
