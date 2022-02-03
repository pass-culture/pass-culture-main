import React from 'react'

import Select from 'components/layout/inputs/Select'
import { ALL_OFFER_TYPE_OPTION } from 'components/pages/Bookings/PreFilters/_constants'
import { OFFER_TYPES } from 'core/Offers'

const { INDIVIDUAL_OR_DUO, EDUCATIONAL } = OFFER_TYPES

interface IOfferType {
  offerType: string
}

interface IFilterByOfferTypeProps {
  selectedOfferType: string
  updateFilters: (value: IOfferType) => void
}

const FilterByOfferType = ({
  updateFilters,
  selectedOfferType,
}: IFilterByOfferTypeProps): JSX.Element => {
  function handleOfferTypeSelection(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const offerType = event.target.value
    updateFilters({ offerType: offerType })
  }

  const offerTypeOptions = [
    { id: INDIVIDUAL_OR_DUO, displayName: 'individuelles' },
    { id: EDUCATIONAL, displayName: 'collectives' },
  ]

  return (
    <Select
      defaultOption={ALL_OFFER_TYPE_OPTION}
      handleSelection={handleOfferTypeSelection}
      label="Type d'offre"
      name="offerType"
      options={offerTypeOptions}
      selectedValue={selectedOfferType}
    />
  )
}

export default FilterByOfferType
