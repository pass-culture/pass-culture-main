import React from 'react'

import strokeLeft from 'icons/stroke-left.svg'
import strokeRight from 'icons/stroke-right.svg'
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
        <SvgIcon src={strokeLeft} alt="Page précédente" />
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
        <SvgIcon src={strokeRight} alt="Page suivante" />
      </button>
    </div>
  ) : null
