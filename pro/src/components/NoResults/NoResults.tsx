import fullRefresh from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoResults.module.scss'

interface NoResultsProps {
  resetFilters: () => void
}

export const NoResults = ({ resetFilters }: NoResultsProps): JSX.Element => (
  <div className={styles['search-no-results']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt="Illustration de recherche"
      className={styles['search-no-results-icon']}
      width="124"
    />
    <p className={styles['search-no-results-title4']}>
      Aucune offre trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifier votre recherche ou
    </p>
    <Button
      variant={ButtonVariant.TERNARYBRAND}
      icon={fullRefresh}
      onClick={resetFilters}
    >
      Afficher toutes les offres
    </Button>
  </div>
)
