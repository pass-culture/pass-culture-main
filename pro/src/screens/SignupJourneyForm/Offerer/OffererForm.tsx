import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue'
import { TextInput } from 'ui-kit'

import styles from './OffererForm.module.scss'

export interface OffererFormValues {
  siret: string
}

const OffererForm = (): JSX.Element => {
  const { setFieldValue } = useFormikContext<OffererFormValues>()

  const formatSiret = async (siret: string): Promise<void> => {
    if ((siret && /^[0-9]+$/.test(unhumanizeSiret(siret))) || !siret) {
      setFieldValue('siret', humanizeSiret(siret))
    }
  }

  return (
    <FormLayout.Section title="Renseignez le SIRET de votre structure">
      <FormLayout.MandatoryInfo className={styles['mandatory-info']} />
      <FormLayout.Row>
        <TextInput
          name="siret"
          label="Numéro de SIRET à 14 chiffres"
          type="text"
          className={styles['input-siret']}
          onChange={e => formatSiret(e.target.value)}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default OffererForm
