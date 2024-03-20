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
  children?: React.ReactNode
}

export const SortArrow = ({
  sortingMode,
  onClick,
  children,
}: SortArrowProps) => (
  <button
    type="button"
    className={styles['sorting-icons']}
    onClick={onClick}
    title={
      sortingMode === SortingMode.NONE
        ? 'Trier'
        : sortingMode === SortingMode.DESC
          ? 'Ne plus trier'
          : 'Trier par ordre décroissant'
    }
  >
    {sortingMode !== SortingMode.NONE ? (
      sortingMode === SortingMode.DESC ? (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullUpIcon}
          alt="Ne plus trier"
          width="10"
        />
      ) : (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullDownIcon}
          alt="Trier par ordre décroissant"
          width="10"
        />
      )
    ) : (
      <span className={cn(styles['sort-icon'], styles['both-icons'])}>
        <SvgIcon src={fullUpIcon} alt="Trier par ordre croissant" width="10" />
        <SvgIcon src={fullDownIcon} alt="" width="10" />
      </span>
    )}
    {children}
  </button>
)
