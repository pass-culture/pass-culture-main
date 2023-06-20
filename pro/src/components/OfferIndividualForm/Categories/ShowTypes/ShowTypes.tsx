import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { Select } from 'ui-kit'

interface IShowTypesProps {
  readOnly?: boolean
}

/* istanbul ignore next: DEBT, TO FIX */
const ShowTypes = ({ readOnly = false }: IShowTypesProps): JSX.Element => {
  const {
    initialValues,
    values: { showType },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()
  const [showTypesOptions, setShowTypesOptions] = useState<{
    showType: SelectOption[]
    showSubType: SelectOption[]
  }>({
    showType: showOptionsTree
      .map(data => ({
        label: data.label,
        value: data.code.toString(),
      }))
      .sort((a, b) => a.label.localeCompare(b.label, 'fr')),
    showSubType: [],
  })

  useEffect(() => {
    setFieldValue('showSubType', initialValues.showSubType)
    let newShowSubTypeOptions: SelectOption[] = []
    if (showType !== FORM_DEFAULT_VALUES.showType) {
      const selectedShowTypeChildren = showOptionsTree.find(
        showTypeOption => showTypeOption.code === parseInt(showType)
      )?.children

      /* istanbul ignore next: DEBT, TO FIX */
      if (selectedShowTypeChildren) {
        newShowSubTypeOptions = selectedShowTypeChildren
          .map(data => ({
            value: data.code.toString(),
            label: data.label,
          }))
          .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
      }
    }

    setShowTypesOptions(prevOptions => {
      return {
        ...prevOptions,
        showSubType: newShowSubTypeOptions,
      }
    })
  }, [showType])

  return (
    <>
      <FormLayout.Row>
        <Select
          label="Type de spectacle"
          name="showType"
          options={showTypesOptions.showType}
          defaultOption={{
            label: 'Choisir un type de spectacle',
            value: FORM_DEFAULT_VALUES.showType,
          }}
          disabled={readOnly}
        />
      </FormLayout.Row>
      {showTypesOptions.showSubType.length > 0 && (
        <FormLayout.Row>
          <Select
            label="Sous-type"
            name="showSubType"
            options={showTypesOptions.showSubType}
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
