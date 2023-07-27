import './NoResultsPage.scss'
import { useFormikContext } from 'formik'
import React, { useContext } from 'react'

import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { FacetFiltersContext } from 'pages/AdageIframe/app/providers'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { SearchFormValues } from '../../OffersSearch'

interface NoResultsPageProps {
  resetForm?: () => void
}

export const NoResultsPage = ({
  resetForm,
}: NoResultsPageProps): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)
  const formik = useFormikContext<SearchFormValues>()

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
      {resetForm &&
        (formik.values.query || facetFilters.length > 1) && ( // la longueur de facetFilters doit être > 1 car il y aura toujours [offer.isEducational:true] dans les facetFilters
          <Button
            icon={fullRefreshIcon}
            className="no-results-button"
            onClick={resetForm}
            variant={ButtonVariant.SECONDARY}
          >
            Réinitialiser les filtres
          </Button>
        )}
    </div>
  )
}
