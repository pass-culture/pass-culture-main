import React, { useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'

import { IBusinessUnit, IBusinessUnitVenue } from '../BusinessUnitList'

interface IBusinessUnitFormProps {
  className?: string
  businessUnit: IBusinessUnit
  onSubmit: (businessUnitId: number, siret: string) => void
  venues: IBusinessUnitVenue[]
}

const BusinessUnitForm = ({
  className,
  businessUnit,
  onSubmit,
  venues,
}: IBusinessUnitFormProps): JSX.Element => {
  const [selectedSIRET, setSelectedSIRET] = useState('')
  const selectOptions = [
    {
      id: '',
      displayName: 'Sélectionner un SIRET dans la liste',
    },
    ...buildSelectOptions(
      'siret',
      'siret',
      venues.filter(venue => venue.siret)
    ),
  ]

  const onChange = (event: { target: { value: string } }) => {
    setSelectedSIRET(event.target.value)
  }

  return (
    <form
      className={className}
      onSubmit={() => onSubmit(businessUnit.id, selectedSIRET)}
    >
      <Select
        handleSelection={onChange}
        label="SIRET de référence"
        name="siret"
        options={selectOptions}
        selectedValue={selectedSIRET}
      />
      <button
        className="primary-button"
        disabled={!selectedSIRET}
        type="submit"
      >
        Valider
      </button>
    </form>
  )
}

export default BusinessUnitForm
