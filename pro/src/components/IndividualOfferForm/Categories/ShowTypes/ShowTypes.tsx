import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { Select } from 'ui-kit/form/Select/Select'

interface ShowTypesProps {
  readOnly?: boolean
}

const getShowSubTypeOptions = (showType: string): SelectOption[] => {
  if (showType === FORM_DEFAULT_VALUES.showType) {
    return []
  }

  const selectedShowTypeChildren = showOptionsTree.find(
    (showTypeOption) => showTypeOption.code === parseInt(showType)
  )?.children

  if (!selectedShowTypeChildren) {
    return []
  }

  return selectedShowTypeChildren
    .map((data) => ({
      value: data.code.toString(),
      label: data.label,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

/* istanbul ignore next: DEBT, TO FIX */
const ShowTypes = ({ readOnly = false }: ShowTypesProps): JSX.Element => {
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

export default ShowTypes
