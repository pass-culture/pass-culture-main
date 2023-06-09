import cn from 'classnames'
import React from 'react'

import { SortingMode } from 'hooks/useColumnSorting'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SortArrow.module.scss'

interface SortArrowProps {
  sortingMode: SortingMode
  onClick: () => void
}

export const SortArrow = ({ sortingMode, onClick }: SortArrowProps) => (
  <button type="button" className={styles['sorting-icons']} onClick={onClick}>
    {sortingMode !== SortingMode.NONE ? (
      sortingMode === SortingMode.DESC ? (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullUpIcon}
          alt="Ne plus trier"
        />
      ) : (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullDownIcon}
          alt="Trier par ordre décroissant"
        />
      )
    ) : (
      <div className={cn(styles['sort-icon'], styles['both-icons'])}>
        <SvgIcon src={fullUpIcon} alt="Trier par ordre croissant" />
        <SvgIcon src={fullDownIcon} alt="" />
      </div>
    )}
  </button>
)
