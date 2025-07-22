import cn from 'classnames'

import { SortingMode } from 'commons/hooks/useColumnSorting'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SortColumn.module.scss'

interface SortColumnProps {
  sortingMode: SortingMode
  onClick: () => void
  children: React.ReactNode
}

export const SortColumn = ({
  sortingMode,
  onClick,
  children,
}: SortColumnProps) => {
  const renderIcon = () => {
    if (sortingMode === SortingMode.DESC) {
      return (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullUpIcon}
          alt="Ne plus trier"
          width="10"
        />
      )
    }

    if (sortingMode === SortingMode.ASC) {
      return (
        <SvgIcon
          className={styles['sort-icon']}
          src={fullDownIcon}
          alt="Trier par ordre décroissant"
          width="10"
        />
      )
    }

    return (
      <span className={cn(styles['sort-icon'], styles['both-icons'])}>
        <SvgIcon src={fullUpIcon} alt="Trier par ordre croissant" width="10" />
        <SvgIcon src={fullDownIcon} alt="" width="10" />
      </span>
    )
  }

  return (
    <button type="button" className={styles['sorting-icons']} onClick={onClick}>
      {children}
      {renderIcon()}
    </button>
  )
}
