import cn from 'classnames'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import fullLeftIcon from '@/icons/full-left.svg'
import fullRightIcon from '@/icons/full-right.svg'
import threeDotsIcon from '@/icons/full-three-dots.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Pagination.module.scss'
import { generateNearestPages } from './utils'

export type PaginationProps = {
  className?: string
  /**
   * The current page number.
   */
  currentPage: number
  /**
   * The total number of pages.
   */
  pageCount: number
  /**
   * Callback function triggered when a page is clicked.
   */
  onPageClick: (page: number) => void
  /**
   * Force the mobile view mode.
   */
  forceMobile?: boolean
}

export const Pagination = ({
  className,
  currentPage,
  pageCount,
  onPageClick,
  forceMobile = false,
}: PaginationProps): JSX.Element | null => {
  const isSmallScreen = useMediaQuery('(max-width: 38.125rem)')
  const isMobile = forceMobile || isSmallScreen

  // At least 2 pages are needed to display something, else we just display nothing
  if (pageCount <= 1) {
    return null
  }

  const isCurrentPage = (page: number) => page === currentPage
  const isFirstPage = currentPage === 1
  const isLastPage = currentPage === pageCount

  const centerPages = generateNearestPages(currentPage, pageCount, { isMobile })

  return (
    <nav
      aria-label="Pagination navigation"
      className={cn(styles['pagination-nav'], className)}
    >
      <ul className={styles['pagination-list']}>
        {/* < Previous page arrow */}
        <li className={styles['pagination-list-item']}>
          <button
            type="button"
            disabled={isFirstPage}
            aria-label={
              !isFirstPage
                ? `Aller à la page précédente (${currentPage - 1} sur ${pageCount})`
                : undefined
            }
            className={cn(
              styles['pagination-link'],
              styles['pagination-link-prev']
            )}
            onClick={() => onPageClick(currentPage - 1)}
          >
            <SvgIcon src={fullLeftIcon} alt="" width="16" />
            {!isMobile && <>Page précédente</>}
          </button>
        </li>

        {/* Always display the first page */}
        <li
          className={styles['pagination-list-item']}
          aria-current={isFirstPage ? 'page' : undefined}
        >
          <button
            type="button"
            aria-label={
              isFirstPage
                ? `Page 1 sur ${pageCount}`
                : `Aller à la page 1 sur ${pageCount}`
            }
            className={cn(styles['pagination-link'], {
              [styles['pagination-link-current']]: isFirstPage,
            })}
            onClick={() => onPageClick(1)}
          >
            1
          </button>
        </li>

        {/* Separation dots (if applicable) */}
        {(centerPages.at(0) as number) > 2 && (
          <li className={styles['pagination-list-item']}>
            <SvgIcon src={threeDotsIcon} alt="" width="16" />
          </li>
        )}

        {/* Current pages and nearest */}
        {centerPages.map((page) => (
          <li
            key={page}
            className={styles['pagination-list-item']}
            aria-current={isCurrentPage(page) ? 'page' : undefined}
          >
            <button
              type="button"
              aria-label={
                isCurrentPage(page)
                  ? `Page ${page} sur ${pageCount}`
                  : `Aller à la page ${page} sur ${pageCount}`
              }
              className={cn(styles['pagination-link'], {
                [styles['pagination-link-current']]: isCurrentPage(page),
              })}
              onClick={() => onPageClick(page)}
            >
              {page}
            </button>
          </li>
        ))}

        {/* Separation dots (if applicable) */}
        {(centerPages.at(-1) as number) < pageCount - 1 && (
          <li className={styles['pagination-list-item']}>
            <SvgIcon src={threeDotsIcon} alt="" width="16" />
          </li>
        )}

        {/* Always display the last page */}
        <li
          className={styles['pagination-list-item']}
          aria-current={isLastPage ? 'page' : undefined}
        >
          <button
            type="button"
            aria-label={
              isLastPage
                ? `Page ${pageCount} sur ${pageCount}`
                : `Aller à la page ${pageCount} sur ${pageCount}`
            }
            className={cn(styles['pagination-link'], {
              [styles['pagination-link-current']]: isLastPage,
            })}
            onClick={() => onPageClick(pageCount)}
          >
            {pageCount}
            <span className={styles['visually-hidden']}>Dernière page</span>
          </button>
        </li>

        {/* Next page arrow > */}
        <li className={styles['pagination-list-item']}>
          <button
            type="button"
            disabled={isLastPage}
            aria-label={
              !isLastPage
                ? `Aller à la page suivante (${currentPage + 1} sur ${pageCount})`
                : undefined
            }
            className={cn(
              styles['pagination-link'],
              styles['pagination-link-next']
            )}
            onClick={() => onPageClick(currentPage + 1)}
          >
            {!isMobile && <>Page suivante</>}
            <SvgIcon src={fullRightIcon} alt="" width="16" />
          </button>
        </li>
      </ul>
    </nav>
  )
}
