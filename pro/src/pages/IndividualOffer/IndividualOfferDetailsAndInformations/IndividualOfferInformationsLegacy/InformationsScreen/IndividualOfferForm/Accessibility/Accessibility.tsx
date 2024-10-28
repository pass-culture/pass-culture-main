import { useFormikContext } from 'formik'
import React from 'react'

import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

import styles from '../IndividualOfferForm.module.scss'

interface AccessiblityProps {
  readOnlyFields?: string[]
}

export const Accessibility = ({
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
