import strokeLeftIcon from '@/icons/stroke-left.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Pagination.module.scss'

/**
 * Props for the Pagination component.
 */
export type PaginationProps = {
  /**
   * The current page number.
   */
  currentPage: number
  /**
   * The total number of pages.
   */
  pageCount: number
  /**
   * Callback function triggered when the previous page button is clicked.
   */
  onPreviousPageClick: () => void
  /**
   * Callback function triggered when the next page button is clicked.
   */
  onNextPageClick: () => void
}

/**
 * The Pagination component allows navigation between different pages of content.
 * It includes buttons to move to the previous or next page, as well as an indicator for the current page.
 *
 * ---
 * **Important: Make sure to handle the `onPreviousPageClick` and `onNextPageClick` callbacks to update the page correctly.**
 * ---
 *
 * @param {PaginationProps} props - The props for the Pagination component.
 * @returns {JSX.Element | null} The rendered Pagination component, or null if there is only one page.
 *
 * @example
 * <Pagination
 *   currentPage={1}
 *   pageCount={5}
 *   onPreviousPageClick={() => console.log('Previous page clicked')}
 *   onNextPageClick={() => console.log('Next page clicked')}
 * />
 *
 * @accessibility
 * - **Button Labels**: The previous and next buttons have descriptive `alt` text, such as "Page précédente" and "Page suivante", to ensure they are accessible to screen readers.
 * - **Disabled State**: Buttons are disabled when the current page is the first or last page to prevent unnecessary navigation.
 */
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
        <SvgIcon src={strokeLeftIcon} alt="Page précédente" width="16" />
      </button>

      <span>
        Page {currentPage}/{pageCount}
      </span>

      <button
        disabled={currentPage >= pageCount}
        onClick={onNextPageClick}
        type="button"
        className={styles['button']}
        data-testid="next-page-button"
      >
        <SvgIcon src={strokeRightIcon} alt="Page suivante" width="16" />
      </button>
    </div>
  ) : null
