import { SortingMode } from '@/commons/hooks/useColumnSorting'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  return (
    <button type="button" className={styles['sorting-icons']} onClick={onClick}>
      {children}

      {sortingMode !== SortingMode.NONE ? (
        sortingMode === SortingMode.DESC ? (
          <SvgIcon src={fullUpIcon} alt="Ne plus trier" width="10" />
        ) : (
          <SvgIcon
            src={fullDownIcon}
            alt="Trier par ordre décroissant"
            width="10"
          />
        )
      ) : (
        <span className={styles['both-icons']}>
          <SvgIcon
            src={fullUpIcon}
            alt="Trier par ordre croissant"
            width="10"
          />
          <SvgIcon src={fullDownIcon} alt="" width="10" />
        </span>
      )}
    </button>
  )
}
