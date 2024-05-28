import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useMemo } from 'react'

import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useAccessibilityOptions } from 'hooks/useAccessibilityOptions'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

import { VenueCreationFormValues } from '../types'

import styles from './Accessibility.module.scss'

export interface AccessiblityProps {
  isCreatingVenue: boolean
  isVenuePermanent?: boolean
}

export const Accessibility = ({
  isCreatingVenue,
  isVenuePermanent,
}: AccessiblityProps) => {
  const { values, setFieldValue, initialValues } = useFormikContext<
    VenueCreationFormValues | VenueEditionFormValues
  >()

  const hasChangedSinceLastSubmit = useMemo(
    () => !isEqual(values.accessibility, initialValues.accessibility),
    [values.accessibility, initialValues.accessibility]
  )

  const FormSectionComponent = isCreatingVenue
    ? FormLayout.Section
    : FormLayout.SubSection

  return (
    <FormSectionComponent title="Modalités d’accessibilité">
      {!isCreatingVenue && isVenuePermanent && (
        <Callout
          links={[
            {
              href: 'https://acceslibre.beta.gouv.fr/',
              label: 'Aller sur acceslibre.beta.gouv.fr ',
              isExternal: true,
            },
          ]}
          variant={CalloutVariant.INFO}
          className={styles['callout']}
        >
          Renseignez facilement les modalités d’accessibilité de votre
          établissement sur la plateforme collaborative acceslibre.beta.gouv.fr
        </Callout>
      )}

      <FormLayout.Row>
        <CheckboxGroup
          group={useAccessibilityOptions(setFieldValue)}
          groupName="accessibility"
          legend="Votre établissement est accessible au public en situation de handicap :"
        />
      </FormLayout.Row>

      {hasChangedSinceLastSubmit && !isCreatingVenue && (
        <>
          <FormLayout.Row>
            <Checkbox
              label="Appliquer le changement à toutes les offres existantes"
              name="isAccessibilityAppliedOnAllOffers"
            />
          </FormLayout.Row>
        </>
      )}
    </FormSectionComponent>
  )
}
