import { CheckboxGroup } from 'ui-kit'
import FormLayout from 'new_components/FormLayout'
import React from 'react'
import { accessibilityOptions } from 'core/shared/accessibilityOptions'
import useAccessibilityUpdates from './useAccessibilityUpdates'

const FormAccessibility = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  useAccessibilityUpdates()

  return (
    <FormLayout.Section title="Accessibilité">
      <FormLayout.Row>
        <CheckboxGroup
          group={accessibilityOptions}
          groupName="accessibility"
          legend="Cette offre est accessible au public en situation de handicap :"
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormAccessibility
