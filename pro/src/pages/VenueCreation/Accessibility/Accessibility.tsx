import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useMemo } from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import FormLayout from 'components/FormLayout'
import { useAccessibilityOptions } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { Checkbox, CheckboxGroup } from 'ui-kit'

import { VenueCreationFormValues } from '../types'

import styles from './Accessibility.module.scss'

interface AccessiblityProps {
  isCreatingVenue: boolean
}

export const Accessibility = ({ isCreatingVenue }: AccessiblityProps) => {
  const isAccesLibreEnabled = useActiveFeature('WIP_ACCESLIBRE')
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
    <FormSectionComponent title="Critères d’accessibilité">
      {isAccesLibreEnabled && (
        <Callout
          title="Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr"
          links={[
            {
              href: 'https://acceslibre.beta.gouv.fr/',
              label: 'Aller sur acceslibre.beta.gouv.fr ',
              isExternal: true,
            },
          ]}
          variant={CalloutVariant.INFO}
          className={styles['callout']}
        />
      )}

      <FormLayout.Row>
        <CheckboxGroup
          group={useAccessibilityOptions(setFieldValue)}
          groupName="accessibility"
          legend="Ce lieu est accessible au public en situation de handicap :"
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
