import React, { useEffect, useState } from 'react'
import { useFormikContext } from 'formik'

import {
  showOptionsTree,
} from 'components/pages/Offers/Offer/OfferDetails/OfferForm/OfferCategories/subTypes'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

import { buildSelectOptions } from '../utils'


interface IType {
  code: number
  label: string
}

interface IOption {
  value: string
  label: string
}

interface IShowTypesOptions {
  showType: IOption[]
  showSubType: IOption[]
}

const initialShowTypesOptions = {
  showType: buildSelectOptions<IType>(c => c.code, c =>c.label, showOptionsTree),
  showSubType: [],
}

const ShowTypes = (): JSX.Element => {
  const { values: { showType } } = useFormikContext<IOfferIndividualFormValues>()
  const [showTypesOptions, setShowTypesOptions] = useState<IShowTypesOptions>(initialShowTypesOptions)

  useEffect(() => {
    if (showType !== FORM_DEFAULT_VALUES.showType) {
      const selectedShowTypeChildren = showOptionsTree.find(
        showTypeOption => showTypeOption.code === parseInt(showType)
      )?.children

      if (selectedShowTypeChildren) {
      setShowTypesOptions(prevOptions => ({
        ...prevOptions,
        showSubType: buildSelectOptions<IType>(
          c => c.code,
          c => c.label,
          selectedShowTypeChildren
        ),
      }))
    }
    } else {
      setShowTypesOptions(prevOptions => ({
        ...prevOptions,
        showSubType: initialShowTypesOptions.showSubType,
      }))
    }
  }, [showType])
  return (
    <>
      <Select
        label='Choisir un type de spectacle'
        name='showType'
        options={showTypesOptions.showType}
        defaultOption={{
          label: 'Choisir un type de spectacle',
          value: FORM_DEFAULT_VALUES.showType,
        }}
      />
      {showType && (
        <Select
          label='Choisir un sous type'
          name='showSubType'
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
