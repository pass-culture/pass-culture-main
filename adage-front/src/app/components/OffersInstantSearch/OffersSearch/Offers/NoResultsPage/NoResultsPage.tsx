import './NoResultsPage.scss'
import React from 'react'

import { Button } from 'app/ui-kit'
import { ReactComponent as MagnifyingGlassIcon } from 'assets/magnifying-glass-no-result.svg'
import { ReactComponent as ResetIcon } from 'assets/reset.svg'

export const NoResultsPage = ({
  handleResetFiltersAndLaunchSearch,
  query,
  facetFilters,
}: {
  handleResetFiltersAndLaunchSearch: () => void
  query: string
  facetFilters
}): JSX.Element => {
  return (
    <div className="no-results">
      <MagnifyingGlassIcon className="no-results-icon" />
      <p className="no-results-text">
        Aucun résultat trouvé pour cette recherche.
      </p>
      {(query || facetFilters.length > 1) && ( // la longueur de facetFilters doit être > 1 car il y aura toujours [offer.isEducational:true] dans les facetFilters
        <Button
          Icon={ResetIcon}
          className="no-results-button"
          classNameIcon="no-results-button-reset-icon"
          label="Réinitialiser tous les filtres"
          onClick={handleResetFiltersAndLaunchSearch}
          variant="secondary"
        />
      )}
    </div>
  )
}
