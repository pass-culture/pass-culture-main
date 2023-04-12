import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { useAccessibilityOptions } from 'hooks'
import { CheckboxGroup } from 'ui-kit'

import styles from '../OfferIndividualForm.module.scss'
import { IOfferIndividualFormValues } from '../types'

interface IAccessiblityProps {
  readOnlyFields?: string[]
}

const Accessibility = ({
  readOnlyFields = [],
}: IAccessiblityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<IOfferIndividualFormValues>()

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
