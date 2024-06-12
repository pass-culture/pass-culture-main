import { Dispatch, SetStateAction } from 'react'

import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InvoicesNoResult.module.scss'
import { FiltersType } from './types'

interface InvoicesNoResultsProps {
  areFiltersDefault: boolean
  initialFilters: FiltersType
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<FiltersType>>
}

export const InvoicesNoResult = ({
  areFiltersDefault,
  initialFilters,
  setAreFiltersDefault,
  setFilters,
}: InvoicesNoResultsProps): JSX.Element => {
  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
  }

  return (
    <div className={styles['no-refunds']}>
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className={styles['no-refunds-icon']}
        width="124"
      />
      <p className={styles['no-refunds-title']}>
        Aucun justificatif de remboursement trouvé pour votre recherche
      </p>
      <p className={styles['no-refunds-description']}>
        Vous pouvez modifier votre recherche ou
        <br />
        <Button
          disabled={areFiltersDefault}
          onClick={resetFilters}
          variant={ButtonVariant.TERNARYPINK}
          icon={fullRefreshIcon}
        >
          Réinitialiser les filtres
        </Button>
      </p>
    </div>
  )
}
