import React, { Dispatch, SetStateAction } from 'react'

import { ReactComponent as SearchSvg } from 'icons/ico-search-gray.svg'

type filtersType = {
  reimbursementPoint: string
  businessUnit: string
  periodStart: Date
  periodEnd: Date
}

interface IInvoicesNoResultsProps {
  areFiltersDefault: boolean
  initialFilters: filtersType
  loadInvoices: (shouldReset: boolean) => void
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<filtersType>>
}

const InvoicesNoResult = ({
  areFiltersDefault,
  initialFilters,
  loadInvoices,
  setAreFiltersDefault,
  setFilters,
}: IInvoicesNoResultsProps): JSX.Element => {
  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
    loadInvoices(true)
  }

  return (
    <div className="no-refunds">
      <SearchSvg />
      <p className="no-refunds-title">
        Aucun justificatif de remboursement trouvé pour votre recherche
      </p>
      <p className="no-refunds-description">
        Vous pouvez modifier votre recherche ou
        <br />
        <button
          className="tertiary-button reset-filters"
          disabled={areFiltersDefault}
          onClick={resetFilters}
          type="button"
        >
          Réinitialiser les filtres
        </button>
      </p>
    </div>
  )
}

export default InvoicesNoResult
