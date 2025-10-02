import { useFormContext } from 'react-hook-form'

import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import {
  type SetAccessibilityFieldValue,
  useAccessibilityOptions,
} from '@/commons/hooks/useAccessibilityOptions'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'

import styles from './FormAccessibility.module.scss'

interface FormAccessibilityProps {
  disableForm: boolean
}

export const FormAccessibility = ({
  disableForm,
}: FormAccessibilityProps): JSX.Element => {
  const { setValue, watch, getFieldState, trigger } =
    useFormContext<OfferEducationalFormValues>()

  const setAccessibilityValue: SetAccessibilityFieldValue = (name, value) => {
    setValue(name, value)
    trigger('accessibility')
  }
  const options = useAccessibilityOptions(
    setAccessibilityValue,
    watch('accessibility')
  )

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        options={options}
        description="Sélectionnez au moins un critère d’accessibilité"
        label="À quel type de handicap votre offre est-elle accessible ?"
        labelTag="h2"
        error={getFieldState('accessibility').error?.message}
        disabled={disableForm}
        variant="detailed"
      />
    </div>
  )
}
