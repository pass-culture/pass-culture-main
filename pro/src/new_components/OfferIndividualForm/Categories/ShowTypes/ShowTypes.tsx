import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

interface IShowTypesProps {
  readOnly?: boolean
}

const ShowTypes = ({ readOnly = false }: IShowTypesProps): JSX.Element => {
  const {
    values: { showType },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()
  const [showTypesOptions, setShowTypesOptions] = useState<{
    showType: SelectOptions
    showSubType: SelectOptions
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
    setFieldValue('showSubType', FORM_DEFAULT_VALUES.showSubType)
    let newShowSubTypeOptions: SelectOptions = []
    if (showType !== FORM_DEFAULT_VALUES.showType) {
      const selectedShowTypeChildren = showOptionsTree.find(
        showTypeOption => showTypeOption.code === parseInt(showType)
      )?.children

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
      <Select
        label="Choisir un type de spectacle"
        name="showType"
        options={showTypesOptions.showType}
        defaultOption={{
          label: 'Choisir un type de spectacle',
          value: FORM_DEFAULT_VALUES.showType,
        }}
        disabled={readOnly}
      />
      {showTypesOptions.showSubType.length > 0 && (
        <Select
          label="Choisir un sous type"
          name="showSubType"
          options={showTypesOptions.showSubType}
          defaultOption={{
            label: 'Choisir un sous type',
            value: FORM_DEFAULT_VALUES.showSubType,
          }}
          disabled={readOnly}
        />
      )}
    </>
  )
}

export default ShowTypes
