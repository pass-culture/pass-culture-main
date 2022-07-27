import { useFormikContext } from 'formik'
import React from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { IAccessibiltyFormValues } from 'core/shared'
import { accessibilityOptions } from 'core/shared/accessibilityOptions'
import { useAccessibilityUpdates } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

interface IFormAccessibilityProps {
  legend?: string
  disableForm: boolean
}

const FormAccessibility = ({
  legend = 'Cette offre est accessible au public en situation de handicap :',
  disableForm,
}: IFormAccessibilityProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const handleAccessibilityChange = (
    newAccessibilityValues: IAccessibiltyFormValues
  ) => setFieldValue('accessibility', newAccessibilityValues)

  useAccessibilityUpdates(values.accessibility, handleAccessibilityChange)

  return (
    <FormLayout.Section title="Accessibilité">
      <FormLayout.Row>
        <CheckboxGroup
          group={accessibilityOptions}
          groupName="accessibility"
          legend={legend}
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormAccessibility
