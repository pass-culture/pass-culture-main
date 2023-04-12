import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import useAccessibilityOptions from 'hooks/useAccessibilityOptions'
import { CheckboxGroup } from 'ui-kit'

interface IFormAccessibilityProps {
  legend?: string
  disableForm: boolean
}

const FormAccessibility = ({
  legend = 'Cette offre est accessible au public en situation de handicap :',
  disableForm,
}: IFormAccessibilityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<IOfferEducationalFormValues>()

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
