import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import { accessibilityOptions } from './accessibilityOptions'

const FormAccessibility = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Cette offre est accessible au public en situation de handicap :"
      title="Accessibilité"
    >
      <FormLayout.Row>
        <CheckboxGroup group={accessibilityOptions} name="accessibility" />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormAccessibility
