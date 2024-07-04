import { useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm/constants'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { Select } from 'ui-kit/form/Select/Select'
import { getShowSubTypeOptions } from 'screens/IndividualOffer/DetailsScreen/utils'

interface ShowTypesProps {
  readOnly?: boolean
}

/* istanbul ignore next: DEBT, TO FIX */
export const ShowTypes = ({
  readOnly = false,
}: ShowTypesProps): JSX.Element => {
  const {
    values: { showType },
  } = useFormikContext<IndividualOfferFormValues>()

  const showTypesOptions = showOptionsTree
    .map((data) => ({
      label: data.label,
      value: data.code.toString(),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  const showSubTypeOptions = getShowSubTypeOptions(showType)

  return (
    <>
      <FormLayout.Row>
        <Select
          label="Type de spectacle"
          name="showType"
          options={showTypesOptions}
          defaultOption={{
            label: 'Choisir un type de spectacle',
            value: FORM_DEFAULT_VALUES.showType,
          }}
          disabled={readOnly}
        />
      </FormLayout.Row>
      {showSubTypeOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            label="Sous-type"
            name="showSubType"
            options={showSubTypeOptions}
            defaultOption={{
              label: 'Choisir un sous-type',
              value: FORM_DEFAULT_VALUES.showSubType,
            }}
            disabled={readOnly}
          />
        </FormLayout.Row>
      )}
    </>
  )
}
