import React from 'react'

import strokeLeftIcon from 'icons/stroke-left.svg'
import strokeRightIcon from 'icons/stroke-right.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Pagination.module.scss'

export type PaginationProps = {
  currentPage: number
  pageCount: number
  onPreviousPageClick: () => void
  onNextPageClick: () => void
}

export const Pagination = ({
  currentPage,
  onPreviousPageClick,
  onNextPageClick,
  pageCount,
}: PaginationProps) =>
  pageCount > 1 ? (
    <div className={styles['pagination']}>
      <button
        disabled={currentPage === 1}
        onClick={onPreviousPageClick}
        type="button"
        className={styles['button']}
      >
        <SvgIcon src={strokeLeftIcon} alt="Page précédente" />
      </button>

      <span>
        Page {currentPage}/{pageCount}
      </span>

      <button
        disabled={currentPage >= pageCount}
        onClick={onNextPageClick}
        type="button"
        className={styles['button']}
      >
        <SvgIcon src={strokeRightIcon} alt="Page suivante" />
      </button>
    </div>
  ) : null
