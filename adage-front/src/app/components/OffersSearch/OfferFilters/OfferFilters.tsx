import React, { useState } from 'react'

import MultiSelectAutocomplete from '../../../ui-kit/MultiSelectAutoComplete'

import { departmentOptions } from './departmentOptions'

import './OfferFilters.scss'
import { Option } from 'app/types'

export const OfferFilters = ({
  className,
}: {
  className?: string
}): JSX.Element => {
  const [departments, setDepartments] = useState<string[]>([])

  const onMultiSelectChange = (selectedOptions: Option[]): void => {
    setDepartments(selectedOptions.map(option => option.value))
  }

  return (
    <div className={className}>
      <span className="offer-filters-title">Filter par :</span>
      <MultiSelectAutocomplete
        label="Département"
        onChange={onMultiSelectChange}
        options={departmentOptions}
      />
    </div>
  )
}
