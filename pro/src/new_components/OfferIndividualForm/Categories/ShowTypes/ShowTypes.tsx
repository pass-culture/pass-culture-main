import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import React, { useEffect, useState } from 'react'

import { Select } from 'ui-kit'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { useFormikContext } from 'formik'

const ShowTypes = (): JSX.Element => {
  const {
    values: { showType },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()
  const [showTypesOptions, setShowTypesOptions] = useState<{
    showType: SelectOptions
    showSubType: SelectOptions
  }>({
    showType: showOptionsTree.map(data => ({
      label: data.label,
      value: data.code.toString(),
    })),
    showSubType: [],
  })

  useEffect(() => {
    setFieldValue('showSubType', FORM_DEFAULT_VALUES.showSubType)
    let newShowSubTypeOptions: SelectOptions = []
    if (showType !== FORM_DEFAULT_VALUES.showType) {
      const selectedMusicTypeChildren = showOptionsTree.find(
        musicTypeOption => musicTypeOption.code === parseInt(showType)
      )?.children

      if (selectedMusicTypeChildren) {
        newShowSubTypeOptions = selectedMusicTypeChildren.map(data => ({
          value: data.code.toString(),
          label: data.label,
        }))
      }
    }

    setShowTypesOptions(prevOptions => {
      return {
        ...prevOptions,
        musicSubType: newShowSubTypeOptions,
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
      />
      {showType && (
        <Select
          label="Choisir un sous type"
          name="showSubType"
          options={showTypesOptions.showSubType}
          defaultOption={{
            label: 'Choisir un sous type',
            value: FORM_DEFAULT_VALUES.showSubType,
          }}
        />
      )}
    </>
  )
}

export default ShowTypes
