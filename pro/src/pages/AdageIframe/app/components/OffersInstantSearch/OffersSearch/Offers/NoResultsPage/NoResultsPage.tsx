import './NoResultsPage.scss'

import React, { useContext } from 'react'

import { ReactComponent as FullRefreshIcon } from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import {
  AlgoliaQueryContext,
  FacetFiltersContext,
} from 'pages/AdageIframe/app/providers'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

export const NoResultsPage = ({
  handleResetFiltersAndLaunchSearch,
}: {
  handleResetFiltersAndLaunchSearch?: () => void
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)
  const { query } = useContext(AlgoliaQueryContext)

  return (
    <div className="no-results">
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className="no-results-icon"
        width="124"
      />
      <p className="no-results-text">
        Aucun résultat trouvé pour cette recherche.
      </p>
      {(query || facetFilters.length > 1) &&
        handleResetFiltersAndLaunchSearch && ( // la longueur de facetFilters doit être > 1 car il y aura toujours [offer.isEducational:true] dans les facetFilters
          <Button
            Icon={FullRefreshIcon}
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
