import './NoResultsPage.scss'
import React, { useContext } from 'react'

import { FacetFiltersContext } from 'app/providers'
import { AlgoliaQueryContext } from 'app/providers/AlgoliaQueryContextProvider'
import { Button } from 'app/ui-kit'
import { ReactComponent as MagnifyingGlassIcon } from 'assets/magnifying-glass-no-result.svg'
import { ReactComponent as ResetIcon } from 'assets/reset.svg'

export const NoResultsPage = ({
  handleResetFiltersAndLaunchSearch,
}: {
  handleResetFiltersAndLaunchSearch: () => void
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)
  const { query } = useContext(AlgoliaQueryContext)

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
