import React, { useState } from 'react'

import { Option } from 'app/types'

import MultiSelectAutocomplete from '../../../ui-kit/MultiSelectAutoComplete'

import { departmentOptions } from './departmentOptions'
import './OfferFilters.scss'

export const OfferFilters = ({
  className,
}: {
  className?: string
}): JSX.Element => {
  // to delete when departments is used
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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
