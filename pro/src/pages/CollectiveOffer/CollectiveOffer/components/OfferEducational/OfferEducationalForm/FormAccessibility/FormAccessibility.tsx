import { useFormikContext } from 'formik'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'

import styles from './FormAccessibility.module.scss'

interface FormAccessibilityProps {
  disableForm: boolean
}

export const FormAccessibility = ({
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setFieldValue, values, getFieldMeta } =
    useFormikContext<OfferEducationalFormValues>()

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        group={useAccessibilityOptions(setFieldValue, values.accessibility)}
        legend={
          <h2 className={styles['subtitle']}>
            À quel type de handicap votre offre est-elle accessible ? *
          </h2>
        }
        name="accessibility"
        error={getFieldMeta('accessibility').error}
        disabled={disableForm}
        required
        asterisk={false}
      />
    </div>
  )
}
