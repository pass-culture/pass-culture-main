import { ALL_OFFER_TYPE_OPTION } from 'core/Bookings'
import { OFFER_TYPES } from 'core/Offers'
import React from 'react'
import Select from 'components/layout/inputs/Select'

const { INDIVIDUAL_OR_DUO, EDUCATIONAL } = OFFER_TYPES

interface IOfferType {
  offerType: string
}

interface IFilterByOfferTypeProps {
  isDisabled: boolean
  selectedOfferType: string
  updateFilters: (value: IOfferType) => void
}

const FilterByOfferType = ({
  isDisabled = false,
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
    { id: INDIVIDUAL_OR_DUO, displayName: 'Individuelles' },
    { id: EDUCATIONAL, displayName: 'Collectives' },
  ]

  return (
    <Select
      defaultOption={ALL_OFFER_TYPE_OPTION}
      handleSelection={handleOfferTypeSelection}
      isDisabled={isDisabled}
      label="Type d’offres"
      name="offerType"
      options={offerTypeOptions}
      selectedValue={selectedOfferType}
    />
  )
}

export default FilterByOfferType
