import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import useAccessibilityOptions from 'hooks/useAccessibilityOptions'
import { CheckboxGroup } from 'ui-kit'

interface FormAccessibilityProps {
  legend?: string
  disableForm: boolean
}

const FormAccessibility = ({
  legend = 'Cette offre est accessible au public en situation de handicap :',
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section title="Accessibilité">
      <FormLayout.Row>
        <CheckboxGroup
          group={useAccessibilityOptions(setFieldValue)}
          groupName="accessibility"
          legend={legend}
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormAccessibility
