import { utcToZonedTime } from 'date-fns-tz'
import React from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { ALL_CATEGORIES_OPTION, ALL_VENUES_OPTION } from 'core/Offers/constants'
import { TSearchFilters } from 'core/Offers/types'
import { getToday } from 'utils/date'

interface ISearchFiltersProps {
  selectedFilters: TSearchFilters
  disableAllFilters: boolean
  storeNameOrIsbnSearchValue: (
    event: React.MouseEvent<HTMLInputElement>
  ) => void
  storeSelectedVenue: (event: React.MouseEvent<HTMLSelectElement>) => void
  storeSelectedCategory: (event: React.MouseEvent<HTMLSelectElement>) => void
  changePeriodBeginningDateValue: (periodBeginningDate: Date) => void
  changePeriodEndingDateValue: (periodEndingDate: Date) => void
  venueOptions: { id: string; displayName: string }[]
  categoriesOptions: { id: string; displayName: string }[]
}

const CollectiveSearchFilters = ({
  selectedFilters,
  disableAllFilters,
  storeNameOrIsbnSearchValue,
  storeSelectedVenue,
  storeSelectedCategory,
  changePeriodBeginningDateValue,
  changePeriodEndingDateValue,
  venueOptions,
  categoriesOptions,
}: ISearchFiltersProps): JSX.Element => {
  return (
    <>
      <TextInput
        disabled={disableAllFilters}
        label="Nom de l’offre"
        name="offre"
        onChange={storeNameOrIsbnSearchValue}
        placeholder="Rechercher par nom d’offre"
        value={selectedFilters.nameOrIsbn}
      />
      <div className="collective-form-row">
        <Select
          defaultOption={ALL_VENUES_OPTION}
          handleSelection={storeSelectedVenue}
          isDisabled={disableAllFilters}
          label="Lieu"
          name="lieu"
          options={venueOptions}
          selectedValue={selectedFilters.venueId}
        />
        <Select
          defaultOption={ALL_CATEGORIES_OPTION}
          handleSelection={storeSelectedCategory}
          isDisabled={disableAllFilters}
          label="Catégories"
          name="categorie"
          options={categoriesOptions}
          selectedValue={selectedFilters.categoryId}
        />
        <PeriodSelector
          changePeriodBeginningDateValue={changePeriodBeginningDateValue}
          changePeriodEndingDateValue={changePeriodEndingDateValue}
          isDisabled={disableAllFilters}
          label="Période de l’évènement"
          periodBeginningDate={
            selectedFilters.periodBeginningDate
              ? utcToZonedTime(selectedFilters.periodBeginningDate, 'UTC')
              : undefined
          }
          periodEndingDate={
            selectedFilters.periodEndingDate
              ? utcToZonedTime(selectedFilters.periodEndingDate, 'UTC')
              : undefined
          }
          todayDate={getToday()}
        />
      </div>
    </>
  )
}

export default CollectiveSearchFilters
