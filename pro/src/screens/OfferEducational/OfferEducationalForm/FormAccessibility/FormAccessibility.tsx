import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit'

import { accessibilityOptions } from './accessibilityOptions'
import styles from './FormAccessibility.module.scss'

const FormAccessibility = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Cette offre est accessibles aux publics en situation de handicap :"
      title="Accessibilité"
    >
      <FormLayout.Row className={styles['checkbox-group']}>
        {accessibilityOptions.map(({ label, value }) => (
          <Checkbox key={value} label={label} name={value} value={value} />
        ))}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormAccessibility
