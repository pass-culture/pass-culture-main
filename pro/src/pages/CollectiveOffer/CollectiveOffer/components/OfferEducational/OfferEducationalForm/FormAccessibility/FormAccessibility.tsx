import { useFormikContext } from 'formik'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface FormAccessibilityProps {
  disableForm: boolean
}

export const FormAccessibility = ({
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section title="À quel type de handicap votre offre est-elle accessible ?">
      <FormLayout.Row>
        <CheckboxGroup
          group={useAccessibilityOptions(setFieldValue)}
          groupName="accessibility"
          legend="Cette offre est accessible au public en situation de handicap :"
          disabled={disableForm}
          variant={CheckboxVariant.BOX}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
