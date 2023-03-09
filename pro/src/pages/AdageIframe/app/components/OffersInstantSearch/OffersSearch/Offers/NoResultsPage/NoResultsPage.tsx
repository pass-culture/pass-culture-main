import './NoResultsPage.scss'

import React, { useContext } from 'react'

import {
  AlgoliaQueryContext,
  FacetFiltersContext,
} from 'pages/AdageIframe/app/providers'
import { ReactComponent as MagnifyingGlassIcon } from 'pages/AdageIframe/assets/magnifying-glass-no-result.svg'
import { ReactComponent as ResetIcon } from 'pages/AdageIframe/assets/reset.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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
          onClick={handleResetFiltersAndLaunchSearch}
          variant={ButtonVariant.SECONDARY}
        >
          Réinitialiser tous les filtres
        </Button>
      )}
    </div>
  )
}
