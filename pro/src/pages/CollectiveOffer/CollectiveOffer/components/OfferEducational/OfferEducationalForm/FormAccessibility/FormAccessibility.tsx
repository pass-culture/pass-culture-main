import { useFormContext } from 'react-hook-form'

import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import { useAccessibilityOptions } from '@/commons/hooks/useAccessibilityOptions'
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

  const { options, onChange, toCheckboxGroupValues } = useAccessibilityOptions(
    async (name: string, value: AccessibilityFormValues) => {
      setValue(
        name as keyof Pick<OfferEducationalFormValues, 'accessibility'>,
        value
      )
      await trigger('accessibility')
    }
  )

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        label="À quel type de handicap votre offre est-elle accessible ? *"
        labelTag="h2"
        options={options}
        value={toCheckboxGroupValues(watch('accessibility'))}
        display="vertical"
        variant="detailed"
        error={getFieldState('accessibility').error?.message}
        disabled={disableForm}
        onChange={onChange}
      />
    </div>
  )
}
