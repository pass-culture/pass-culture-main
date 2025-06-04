import { useFormikContext } from 'formik'
import { useMemo } from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { isEqual } from 'commons/utils/isEqual'
import { ExternalAccessibility } from 'components/ExternalAccessibility/ExternalAccessibility'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { AccessibilityCallout } from 'pages/VenueEdition/AccessibilityCallout/AccessibilityCallout'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'

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
  const { values, setFieldValue, initialValues, getFieldMeta } =
    useFormikContext<VenueEditionFormValues>()
  const checkboxGroup = useAccessibilityOptions(
    setFieldValue,
    values.accessibility
  )

  const hasChangedSinceLastSubmit = useMemo(
    () => !isEqual(values.accessibility, initialValues.accessibility),
    [values.accessibility, initialValues.accessibility]
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
              group={checkboxGroup}
              name="accessibility"
              required
              legend="Votre établissement est accessible au public en situation de handicap :"
              error={getFieldMeta('accessibility').error}
            />
          </FormLayout.Row>
          {hasChangedSinceLastSubmit && (
            <FormLayout.Row>
              <Checkbox
                label="Appliquer le changement à toutes les offres existantes"
                checked={values.isAccessibilityAppliedOnAllOffers}
                onChange={(e) =>
                  setFieldValue(
                    'isAccessibilityAppliedOnAllOffers',
                    e.target.checked
                  )
                }
                name="isAccessibilityAppliedOnAllOffers"
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
