import React, { useState } from 'react'

import Select from 'components/layout/inputs/Select'
import { sortByDisplayName } from 'utils/strings'

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
    ...sortByDisplayName(
      venues
        .filter(item => item['siret'] !== null)
        .map(item => {
          return {
            id: item.siret as string,
            displayName: item['siret'] as string,
          }
        })
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
