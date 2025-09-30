import { useFormContext } from 'react-hook-form'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAccessibilityOptions } from '@/commons/hooks/useAccessibilityOptions'
import { isEqual } from '@/commons/utils/isEqual'
import { ExternalAccessibility } from '@/components/ExternalAccessibility/ExternalAccessibility'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { AccessibilityCallout } from '@/pages/VenueEdition/AccessibilityCallout/AccessibilityCallout'
import type { VenueEditionFormValues } from '@/pages/VenueEdition/types'

import styles from './AccessibilityForm.module.scss'

export interface AccessiblityFormProps {
  isVenuePermanent?: boolean
  externalAccessibilityId: GetVenueResponseModel['externalAccessibilityId']
  externalAccessibilityData: GetVenueResponseModel['externalAccessibilityData']
  isSubSubSection?: boolean
}

export const AccessibilityForm = ({
  isVenuePermanent,
  externalAccessibilityId,
  externalAccessibilityData,
  isSubSubSection,
}: AccessiblityFormProps) => {
  const { watch, setValue, formState, trigger } =
    useFormContext<VenueEditionFormValues>()

  const values = watch()

  const {
    options: accessibilityOptions,
    onChange: onAccessibilityCheckboxGroupChange,
    toCheckboxGroupValues: toAccessibilityCheckboxGroupValues,
  } = useAccessibilityOptions(
    async (_: string, value: VenueEditionFormValues['accessibility']) => {
      setValue('accessibility', value)
      await trigger('accessibility')
    }
  )

  const hasChangedSinceLastSubmit = !isEqual(
    values.accessibility,
    formState.defaultValues?.accessibility
  )

  const isAccessibilityDefinedViaAccesLibre = !!externalAccessibilityData
  const title = isAccessibilityDefinedViaAccesLibre
    ? 'Modalités d’accessibilité via acceslibre'
    : 'Modalités d’accessibilité'

  const FormLayoutSection = isSubSubSection
    ? FormLayout.SubSubSection
    : FormLayout.SubSection

  return (
    <FormLayoutSection title={title}>
      {isAccessibilityDefinedViaAccesLibre ? (
        <ExternalAccessibility
          externalAccessibilityId={externalAccessibilityId}
          externalAccessibilityData={externalAccessibilityData}
        />
      ) : (
        <>
          <FormLayout.Row>
            <CheckboxGroup
              options={accessibilityOptions}
              value={toAccessibilityCheckboxGroupValues(values.accessibility)}
              label="Votre établissement est accessible au public en situation de handicap :"
              error={formState.errors.accessibility?.message}
              onChange={onAccessibilityCheckboxGroupChange}
            />
          </FormLayout.Row>
          {hasChangedSinceLastSubmit && (
            <FormLayout.Row>
              <Checkbox
                label="Appliquer le changement à toutes les offres existantes"
                checked={values.isAccessibilityAppliedOnAllOffers}
                onChange={(e) =>
                  setValue(
                    'isAccessibilityAppliedOnAllOffers',
                    e.target.checked
                  )
                }
                className={styles['apply-on-all-offers-checkbox']}
              />
            </FormLayout.Row>
          )}
          {isVenuePermanent && (
            <AccessibilityCallout className={styles['callout']} />
          )}
        </>
      )}
    </FormLayoutSection>
  )
}
