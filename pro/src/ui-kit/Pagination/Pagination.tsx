import classNames from 'classnames'

import strokeLeftIcon from 'icons/stroke-left.svg'
import strokeRightIcon from 'icons/stroke-right.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Pagination.module.scss'

export type PaginationProps = {
  currentPage: number
  pageCount: number
  onPreviousPageClick: () => void
  onNextPageClick: () => void
  onPageClick: (page: number) => void
}

const range = (start: number, end: number) => {
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
}

export const Pagination = ({
  currentPage,
  pageCount,
  onPreviousPageClick,
  onNextPageClick,
  onPageClick,
}: PaginationProps) => {
  if (pageCount <= 1) {
    return null
  }

  const siblingCount = 1
  const firstPage = 1
  const lastPage = pageCount

  const startPages = range(firstPage, Math.min(firstPage + 1, pageCount))
  const endPages = range(Math.max(lastPage - 1, firstPage), lastPage)

  const siblingsStart = Math.max(
    Math.min(currentPage - siblingCount, pageCount - siblingCount * 2 - 1),
    firstPage + 2
  )

  const siblingsEnd = Math.min(
    Math.max(currentPage + siblingCount, siblingCount * 2 + 2),
    lastPage - 2
  )

  const pages = [
    ...startPages,
    ...(siblingsStart > firstPage + 2 ? ['ellipsis-start'] : []),
    ...range(siblingsStart, siblingsEnd),
    ...(siblingsEnd < lastPage - 2 ? ['ellipsis-end'] : []),
    ...endPages,
  ]

  return (
    <nav
      className={styles.pagination}
      role="navigation"
      aria-label="Pagination"
    >
      <ul className={styles.list}>
        <li>
          <button
            className={styles.link}
            onClick={() => onPageClick(1)}
            disabled={currentPage === 1}
            aria-label="Première page"
          >
            {'|<'}
          </button>
        </li>
        <li>
          <button
            className={styles.link}
            onClick={onPreviousPageClick}
            disabled={currentPage === 1}
            aria-label="Page précédente"
          >
            <SvgIcon src={strokeLeftIcon} alt="Page précédente" width="16" />
            <span className={styles.label}>Précédent</span>
          </button>
        </li>

        {pages.map((page, index) => (
          <li key={index}>
            {typeof page === 'number' ? (
              <button
                className={classNames(styles.link, {
                  [styles.current]: page === currentPage,
                })}
                onClick={() => onPageClick(page)}
                aria-label={`Page ${page}`}
                aria-current={page === currentPage ? 'page' : undefined}
              >
                {page}
              </button>
            ) : (
              <span className={styles.ellipsis} aria-hidden="true">
                …
              </span>
            )}
          </li>
        ))}

        <li>
          <button
            className={styles.link}
            onClick={onNextPageClick}
            disabled={currentPage === pageCount}
            aria-label="Page suivante"
          >
            <span className={styles.label}>Suivant</span>
            <SvgIcon src={strokeRightIcon} alt="Page suivante" width="16" />
          </button>
        </li>
        <li>
          <button
            className={styles.link}
            onClick={() => onPageClick(pageCount)}
            disabled={currentPage === pageCount}
            aria-label="Dernière page"
          >
            {'>|'}
          </button>
        </li>
      </ul>
    </nav>
  )
}
