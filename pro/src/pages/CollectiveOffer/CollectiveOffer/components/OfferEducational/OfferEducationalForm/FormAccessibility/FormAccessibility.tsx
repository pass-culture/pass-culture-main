import { useFormikContext } from 'formik'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

import styles from './FormAccessibility.module.scss'

interface FormAccessibilityProps {
  disableForm: boolean
}

export const FormAccessibility = ({
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setFieldValue } = useFormikContext<OfferEducationalFormValues>()

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        group={useAccessibilityOptions(setFieldValue)}
        legend={
          <h2 className={styles['subtitle']}>
            À quel type de handicap votre offre est-elle accessible ? *
          </h2>
        }
        hideAsterisk
        groupName="accessibility"
        disabled={disableForm}
      />
    </div>
  )
}
