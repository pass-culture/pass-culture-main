import React from 'react'

import Icon from 'ui-kit/Icon/Icon'

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
        <Icon alt="Page précédente" svg="ico-left-arrow" />
      </button>

      <span>
        Page {currentPage}/{pageCount}
      </span>

      <button
        disabled={currentPage === pageCount}
        onClick={onNextPageClick}
        type="button"
        className={styles['button']}
      >
        <Icon alt="Page suivante" svg="ico-right-arrow" />
      </button>
    </div>
  ) : null
