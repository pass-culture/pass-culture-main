import { useFormikContext } from 'formik'
import React from 'react'

import { AccessiblityEnum, IAccessibiltyFormValues } from 'core/shared'
import { accessibilityOptions } from 'core/shared/accessibilityOptions'
import { useAccessibilityUpdates } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { CheckboxGroup } from 'ui-kit'

import styles from '../OfferIndividualForm.module.scss'
import { IOfferIndividualFormValues } from '../types'

interface IAccessiblityProps {
  readOnlyFields?: string[]
}

const Accessibility = ({
  readOnlyFields = [],
}: IAccessiblityProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferIndividualFormValues>()

  const accessibilityValues = {
    [AccessiblityEnum.VISUAL]: values.accessibility[AccessiblityEnum.VISUAL],
    [AccessiblityEnum.MENTAL]: values.accessibility[AccessiblityEnum.MENTAL],
    [AccessiblityEnum.AUDIO]: values.accessibility[AccessiblityEnum.AUDIO],
    [AccessiblityEnum.MOTOR]: values.accessibility[AccessiblityEnum.MOTOR],
    [AccessiblityEnum.NONE]: values.accessibility[AccessiblityEnum.NONE],
  }
  const handleAccessibilityChange = (
    newAccessibilityValues: IAccessibiltyFormValues
  ) => setFieldValue('accessibility', newAccessibilityValues)

  useAccessibilityUpdates(accessibilityValues, handleAccessibilityChange)

  return (
    <FormLayout.Section title="Accessibilité">
      <FormLayout.Row>
        <CheckboxGroup
          className={styles['accessibility-checkbox-group']}
          group={accessibilityOptions}
          groupName="accessibility"
          disabled={readOnlyFields.includes('accessibility')}
          legend="Cette offre est accessible au public en situation de handicap :"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default Accessibility
