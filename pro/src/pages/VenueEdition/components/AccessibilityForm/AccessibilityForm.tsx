import { useFormContext } from 'react-hook-form'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { isEqual } from '@/commons/utils/isEqual'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { ExternalAccessibility } from '@/components/ExternalAccessibility/ExternalAccessibility'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'

import type { VenueEditionFormValues } from '../../commons/types'
import { AccessibilityCallout } from '../AccessibilityCallout/AccessibilityCallout'
import styles from './AccessibilityForm.module.scss'

export interface AccessiblityFormProps {
  externalAccessibilityId: GetVenueResponseModel['externalAccessibilityId']
  externalAccessibilityData: GetVenueResponseModel['externalAccessibilityData']
  isSubSubSection?: boolean
}

export const AccessibilityForm = ({
  externalAccessibilityId,
  externalAccessibilityData,
  isSubSubSection,
}: AccessiblityFormProps) => {
  const { watch, setValue, formState } =
    useFormContext<VenueEditionFormValues>()

  const values = watch()

  const checkboxGroup = updateAccessibilityField(setValue, values.accessibility)

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
              options={checkboxGroup}
              label="Votre établissement est accessible au public en situation de handicap :"
              description="Sélectionnez au moins une option"
              variant="detailed"
              error={formState.errors.accessibility?.message}
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
          <AccessibilityCallout className={styles['callout']} />
        </>
      )}
    </FormLayoutSection>
  )
}
