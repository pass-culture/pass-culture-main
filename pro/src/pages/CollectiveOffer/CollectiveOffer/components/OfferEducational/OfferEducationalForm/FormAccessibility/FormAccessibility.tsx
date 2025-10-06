import { useFormContext } from 'react-hook-form'

import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
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

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        options={useAccessibilityOptions(
          async (name: string, value: string) => {
            setValue(name as keyof OfferEducationalFormValues, value)
            await trigger('accessibility')
          },
          watch('accessibility')
        )}
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
