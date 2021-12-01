import React from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'

import { IBusinessUnit, IBusinessUnitVenue } from '../BusinessUnitList'

interface IBusinessUnitFormProps {
  className?: string
  businessUnit: IBusinessUnit
  onSubmit: () => void
  venues: IBusinessUnitVenue[]
}

const BusinessUnitForm = ({
  className,
  businessUnit,
  onSubmit,
  venues,
}: IBusinessUnitFormProps) => {
  const selectOptions = [
    {
      id: '',
      displayName: 'Choix du lieu',
    },
    ...buildSelectOptions('name', 'siret', venues.filter((venue) => venue.siret))
  ]

  const onChange = () => {

  }

  return (
    <div className={className}>
      <Select
        label="Siret de reference du point de facturation :"
        name="siret"
        handleSelection={onChange}
        options={selectOptions}
        selectedValue=""
      />
    </div>
  )
}

export default BusinessUnitForm