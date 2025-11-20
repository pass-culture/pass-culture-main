import { useFormContext } from 'react-hook-form'

import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'

import styles from './FormAccessibility.module.scss'

interface FormAccessibilityProps {
  disableForm: boolean
}

export const FormAccessibility = ({
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setValue, watch, getFieldState } =
    useFormContext<OfferEducationalFormValues>()

  const options = updateAccessibilityField(setValue, watch('accessibility'))

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        options={options}
        description="Sélectionnez au moins une option"
        label={
          <h2 className={styles['checkbox-group-title']}>
            À quel type de handicap votre offre est-elle accessible ?
          </h2>
        }
        error={getFieldState('accessibility').error?.message}
        disabled={disableForm}
        variant="detailed"
      />
    </div>
  )
}
