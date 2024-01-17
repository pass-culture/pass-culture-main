import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useMemo } from 'react'

import Callout from 'components/Callout/Callout'
import FormLayout from 'components/FormLayout'
import { useAccessibilityOptions } from 'hooks'
import fullLinkIcon from 'icons/full-link.svg'
import { Checkbox, CheckboxGroup } from 'ui-kit'

import { VenueFormValues } from '..'
interface AccessiblityProps {
  isCreatingVenue: boolean
}

const Accessibility = ({ isCreatingVenue }: AccessiblityProps) => {
  const { values, setFieldValue, initialValues } =
    useFormikContext<VenueFormValues>()

  const hasChangedSinceLastSubmit = useMemo(
    () => !isEqual(values.accessibility, initialValues.accessibility),
    [values.accessibility, initialValues.accessibility]
  )

  return (
    <FormLayout.Section title="Accessibilité du lieu">
      <FormLayout.Row
        sideComponent={
          <Callout
            links={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4412007286289--Acteurs-Culturels-Comment-indiquer-les-conditions-d-accessibilit%C3%A9-d-une-offre-sur-le-pass-Culture-',
                linkTitle: 'Comment indiquer les conditions d’accès ?',
                icon: fullLinkIcon,
              },
            ]}
          >
            Les modalités d’accessibilité s’appliqueront par défaut à la
            création de vos offres. Vous pourrez modifier cette information à
            l’échelle de chaque offre.
          </Callout>
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

export default Accessibility
