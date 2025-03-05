import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import { useMemo } from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { ExternalAccessibility } from 'components/ExternalAccessibility/ExternalAccessibility'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { AccessibilityCallout } from 'pages/VenueEdition/AccessibilityCallout/AccessibilityCallout'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

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
  const { values, setFieldValue, initialValues } = useFormikContext<VenueEditionFormValues>()
  const checkboxGroup = useAccessibilityOptions(setFieldValue)

  const hasChangedSinceLastSubmit = useMemo(
    () => !isEqual(values.accessibility, initialValues.accessibility),
    [values.accessibility, initialValues.accessibility]
  )

  const isAccessibilityDefinedViaAccesLibre = !!externalAccessibilityData
  const title = isAccessibilityDefinedViaAccesLibre ?
    'Modalités d’accessibilité via acceslibre' :
    'Modalités d’accessibilité'

  const FormLayoutSection = isSubSubSection ? FormLayout.SubSubSection : FormLayout.SubSection

  return (
    <FormLayoutSection title={title}>
      {
        isAccessibilityDefinedViaAccesLibre
          ? <ExternalAccessibility
              externalAccessibilityId={externalAccessibilityId}
              externalAccessibilityData={externalAccessibilityData}
            />
          : <>
              <FormLayout.Row>
                <CheckboxGroup
                  group={checkboxGroup}
                  groupName="accessibility"
                  legend="Votre établissement est accessible au public en situation de handicap :"
                />
              </FormLayout.Row>
              {hasChangedSinceLastSubmit && (
                <FormLayout.Row>
                  <Checkbox
                    label="Appliquer le changement à toutes les offres existantes"
                    name="isAccessibilityAppliedOnAllOffers"
                    className={styles['apply-on-all-offers-checkbox']}
                  />
                </FormLayout.Row>
              )}
              {isVenuePermanent && <AccessibilityCallout className={styles['callout']} />}
            </>
      }
    </FormLayoutSection>
  )
}
