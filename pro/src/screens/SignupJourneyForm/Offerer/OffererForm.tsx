import { useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue/utils'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './OffererForm.module.scss'

export interface OffererFormValues {
  siret: string
}

interface OffererFormProps {
  setShowInvisibleBanner: (showBanner: boolean) => void
}

export const OffererForm = ({
  setShowInvisibleBanner,
}: OffererFormProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<OffererFormValues>()

  const formatSiret = async (siret: string): Promise<void> => {
    setShowInvisibleBanner(false)
    if ((siret && /^[0-9]+$/.test(unhumanizeSiret(siret))) || !siret) {
      await setFieldValue('siret', humanizeSiret(siret))
    }
  }

  return (
    <FormLayout.Section>
      <h1>Renseignez le SIRET de votre structure</h1>
      <FormLayout.MandatoryInfo className={styles['mandatory-info']} />
      <FormLayout.Row>
        <TextInput
          name="siret"
          label="Numéro de SIRET à 14 chiffres"
          type="text"
          className={styles['input-siret']}
          onChange={(e) => formatSiret(e.target.value)}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
