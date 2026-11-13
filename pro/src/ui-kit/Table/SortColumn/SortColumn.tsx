import { useId } from 'react'

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

const sortingDescriptions = {
  [SortingMode.NONE]: 'Aucun tri appliqué à cette colonne.',
  [SortingMode.ASC]: 'Tri actuel : ordre croissant.',
  [SortingMode.DESC]: 'Tri actuel : ordre décroissant.',
}

const withSortingMode = (sortingMode: SortingMode) => {
  return sortingMode === SortingMode.DESC ? (
    <SvgIcon src={fullUpIcon} alt="Cliquez pour ne plus trier" width="10" />
  ) : (
    <SvgIcon
      src={fullDownIcon}
      alt="Cliquez pour trier par ordre décroissant"
      width="10"
    />
  )
}

export const SortColumn = ({
  sortingMode,
  onClick,
  children,
}: SortColumnProps) => {
  const sortingDescriptionId = useId()

  return (
    <>
      <button
        type="button"
        className={styles['sorting-icons']}
        onClick={onClick}
        aria-describedby={sortingDescriptionId}
      >
        {children}{' '}
        {sortingMode !== SortingMode.NONE ? (
          withSortingMode(sortingMode)
        ) : (
          <span className={styles['both-icons']}>
            <SvgIcon
              src={fullUpIcon}
              alt="Cliquez pour trier par ordre croissant"
              width="10"
            />
            <SvgIcon src={fullDownIcon} alt="" width="10" />
          </span>
        )}
      </button>
      <p id={sortingDescriptionId} className={styles['visually-hidden']}>
        {sortingDescriptions[sortingMode]}
      </p>
    </>
  )
}
