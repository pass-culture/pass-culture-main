import React, { Dispatch, SetStateAction } from 'react'

import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { FiltersType } from './types'

interface InvoicesNoResultsProps {
  areFiltersDefault: boolean
  initialFilters: FiltersType
  loadInvoices: (shouldReset: boolean) => void
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<FiltersType>>
}

const InvoicesNoResult = ({
  areFiltersDefault,
  initialFilters,
  loadInvoices,
  setAreFiltersDefault,
  setFilters,
}: InvoicesNoResultsProps): JSX.Element => {
  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
    loadInvoices(true)
  }

  return (
    <div className="no-refunds">
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className="no-refunds-icon"
        width="124"
      />
      <p className="no-refunds-title">
        Aucun justificatif de remboursement trouvé pour votre recherche
      </p>
      <p className="no-refunds-description">
        Vous pouvez modifier votre recherche ou
        <br />
        <Button
          disabled={areFiltersDefault}
          onClick={resetFilters}
          type="button"
          variant={ButtonVariant.TERNARYPINK}
        >
          Réinitialiser les filtres
        </Button>
      </p>
    </div>
  )
}

export default InvoicesNoResult
