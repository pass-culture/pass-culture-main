import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useMemo } from 'react'

import FormLayout from 'components/FormLayout'
import { useAccessibilityOptions } from 'hooks'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { Checkbox, CheckboxGroup, InfoBox } from 'ui-kit'

import { VenueCreationFormValues } from '../types'

interface AccessiblityProps {
  isCreatingVenue: boolean
}

export const Accessibility = ({ isCreatingVenue }: AccessiblityProps) => {
  const { values, setFieldValue, initialValues } = useFormikContext<
    VenueCreationFormValues | VenueEditionFormValues
  >()

  const hasChangedSinceLastSubmit = useMemo(
    () => !isEqual(values.accessibility, initialValues.accessibility),
    [values.accessibility, initialValues.accessibility]
  )

  return (
    <FormLayout.Section title="Critères d’accessibilité">
      <FormLayout.Row
        sideComponent={
          <InfoBox
            link={{
              text: 'En savoir plus',
              to: 'https://aide.passculture.app/hc/fr/articles/4412007286289--Acteurs-Culturels-Comment-indiquer-les-conditions-d-accessibilit%C3%A9-d-une-offre-sur-le-pass-Culture-',
              isExternal: true,
              'aria-label': 'en savoir plus sur les modalités d’accessibilité',
            }}
          >
            Les modalités d’accessibilité s’appliqueront par défaut à la
            création de vos offres. Vous pourrez modifier cette information à
            l’échelle de chaque offre.
          </InfoBox>
        }
      >
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
    </FormLayout.Section>
  )
}
