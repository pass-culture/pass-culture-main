import React from 'react'

import { SortingMode } from 'hooks/useColumnSorting'
import Icon from 'ui-kit/Icon/Icon'

import styles from './SortArrow.module.scss'

interface SortArrowProps {
  sortingMode: SortingMode
  onClick: () => void
}

export const SortArrow = ({ sortingMode, onClick }: SortArrowProps) => (
  <button className={styles['sorting-icons']} onClick={onClick}>
    {sortingMode !== SortingMode.NONE ? (
      sortingMode === SortingMode.DESC ? (
        <Icon alt="Ne plus trier" svg="ico-arrow-up-r" />
      ) : (
        <Icon alt="Trier par ordre décroissant" svg="ico-arrow-down-r" />
      )
    ) : (
      <Icon alt="Trier par ordre croissant" svg="ico-unfold" />
    )}
  </button>
)
