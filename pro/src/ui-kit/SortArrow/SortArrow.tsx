import cn from 'classnames'

import { SortingMode } from 'commons/hooks/useColumnSorting'
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
  <button type="button" className={styles['sorting-icons']} onClick={onClick}>
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
