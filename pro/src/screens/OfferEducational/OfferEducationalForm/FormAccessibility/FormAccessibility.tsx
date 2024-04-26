import { useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import useAccessibilityOptions from 'hooks/useAccessibilityOptions'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

interface FormAccessibilityProps {
  legend?: string
  disableForm: boolean
}

export const FormAccessibility = ({
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
