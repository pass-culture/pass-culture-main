import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { useAccessibilityOptions } from 'hooks'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

import styles from '../IndividualOfferForm.module.scss'
import { IndividualOfferFormValues } from '../types'

interface AccessiblityProps {
  readOnlyFields?: string[]
}

const Accessibility = ({
  readOnlyFields = [],
}: AccessiblityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<IndividualOfferFormValues>()

  return (
    <FormLayout.Section title="Accessibilité">
      <FormLayout.Row>
        <CheckboxGroup
          className={styles['accessibility-checkbox-group']}
          group={useAccessibilityOptions(setFieldValue)}
          groupName="accessibility"
          disabled={readOnlyFields.includes('accessibility')}
          legend="Cette offre est accessible au public en situation de handicap :"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default Accessibility
