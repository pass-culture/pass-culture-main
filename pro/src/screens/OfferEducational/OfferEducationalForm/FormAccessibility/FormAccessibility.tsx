import React from 'react'

import { Checkbox } from 'ui-kit'

import FormSection from '../FormSection'

import { accessibilityOptions } from './accessibilityOptions'
import styles from './FormAccessibility.module.scss'

const FormAccessibility = (): JSX.Element => {
  return (
    <FormSection
      subtitle="Cette offre est accessibles aux publics en situation de handicap :"
      title="Accessibilité"
    >
      <div className={styles.checkboxGroup}>
        {accessibilityOptions.map(({ label, value }) => (
          <Checkbox
            key={value}
            label={label}
            name='accessibility'
            value={value}
          />
        ))}

      </div>
    </FormSection>
  )
}

export default FormAccessibility
