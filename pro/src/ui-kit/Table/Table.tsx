import classNames from 'classnames'
import React, { useMemo, useState } from 'react'

import { SortingMode, useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import {
  Pagination,
  type PaginationProps,
} from '@/design-system/Pagination/Pagination'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { SortColumn } from './SortColumn/SortColumn'
import styles from './Table.module.scss'
import { TableNoData } from './TableNoData/TableNoData'
import { TableNoFilterResult } from './TableNoFilterResult/TableNoFilterResult'

export enum TableVariant {
  COLLAPSE = 'collapse',
  SEPARATE = 'separate',
}

type NoResultProps = {
  message: string
  subtitle?: string
  resetMessage?: string
  onFilterReset: () => void
}

type EmptyStateProps = {
  hasNoData: boolean
  message: {
    icon: string
    title: string
    subtitle: string
  }
}

export interface Column<T> {
  id: string
  label: string
  sortable?: boolean
  ordererField?: keyof T | ((row: T) => React.ReactNode)
  render?: (row: T) => React.ReactNode
  headerColSpan?: number
  bodyHidden?: boolean
  headerHidden?: boolean
  /** Visual header content (can be any React node, e.g., a component) */
  header?: React.ReactNode
}

interface TableProps<T extends { id: string | number }> {
  title?: string
  columns: Column<T>[]
  data: T[]
  allData?: T[]
  selectable?: boolean
  className?: string
  isLoading: boolean
  isSticky?: boolean
  variant: TableVariant
  selectedNumber?: string
  selectedIds?: Set<string | number>
  onSelectionChange?: (rows: T[]) => void
  getFullRowContent?: (row: T) => React.ReactNode | null
  isRowSelectable?: (row: T) => boolean
  noResult: NoResultProps
  noData: EmptyStateProps
  pagination?: PaginationProps
}

function getValue<T>(
  row: T,
  ordererField?: keyof T | string | ((r: T) => unknown)
) {
  if (!ordererField) {
    return undefined
  }
  if (typeof ordererField === 'function') {
    return ordererField(row)
  }
  if (typeof ordererField === 'string') {
    // biome-ignore lint/suspicious/noExplicitAny: Difficult to type.
    return ordererField.split('.').reduce<any>((obj, key) => obj?.[key], row)
  }
  return row[ordererField]
}

export function Table<
  T extends {
    name?: string
    id: string | number
  },
>({
  title = 'Tableau de données',
  columns,
  data,
  allData,
  selectable = false,
  selectedNumber,
  selectedIds: controlledSelectedIds,
  className,
  isLoading,
  isSticky,
  variant,
  noResult,
  noData,
  onSelectionChange,
  getFullRowContent,
  isRowSelectable,
  pagination,
}: TableProps<T>) {
  const fullScope = allData ?? data

  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<unknown>()

  const [uncontrolledSelectedIds, setUncontrolledSelectedIds] = useState<
    Set<string | number>
  >(new Set())

  const isControlled = controlledSelectedIds !== undefined
  const selectedIds = isControlled
    ? controlledSelectedIds
    : uncontrolledSelectedIds

  const updateSelectedIds = (newSelectedIds: Set<string | number>) => {
    if (!isControlled) {
      setUncontrolledSelectedIds(newSelectedIds)
    }
    // 🔁 notify with rows from the FULL scope (all pages)
    onSelectionChange?.(fullScope.filter((r) => newSelectedIds.has(r.id)))
  }

  function sortTableColumn(col: unknown) {
    onColumnHeaderClick(col)
  }

  const selectableRowsAll = useMemo(
    () => (isRowSelectable ? fullScope.filter(isRowSelectable) : fullScope),
    [fullScope, isRowSelectable]
  )

  const toggleSelectAll = () => {
    if (selectedIds.size === selectableRowsAll.length) {
      updateSelectedIds(new Set())
    } else {
      updateSelectedIds(new Set(selectableRowsAll.map((r) => r.id)))
    }
  }

  const toggleSelectRow = (row: T) => {
    const newSet = new Set(selectedIds)
    newSet.has(row.id) ? newSet.delete(row.id) : newSet.add(row.id)
    updateSelectedIds(newSet)
  }

  const sortedData = useMemo(() => {
    if (!currentSortingColumn) {
      return data
    }
    const col = columns.find((c) => c.id === currentSortingColumn)
    if (!col) {
      return data
    }

    return [...fullScope].sort((a, b) => {
      const valueA = getValue(a, col.ordererField)
      const valueB = getValue(b, col.ordererField)
      if (valueA === valueB) {
        return 0
      }
      return valueA < valueB
        ? currentSortingMode === SortingMode.ASC
          ? -1
          : 1
        : currentSortingMode === SortingMode.ASC
          ? 1
          : -1
    })
  }, [data, currentSortingColumn, currentSortingMode, columns, fullScope])

  // Header checkbox state based on ALL pages
  const headerChecked =
    selectedIds.size === selectableRowsAll.length &&
    selectableRowsAll.length > 0

  const headerIndeterminate =
    selectedIds.size > 0 && selectedIds.size < selectableRowsAll.length

  const headerLabel = headerChecked
    ? 'Tout désélectionner'
    : 'Tout sélectionner'

  if (noData.hasNoData) {
    return <TableNoData noData={noData.message} />
  }

  return (
    <div className={classNames(styles.wrapper, className)}>
      {selectable && (
        <div className={styles['table-select-all']}>
          <Checkbox
            label={headerLabel}
            checked={headerChecked}
            indeterminate={headerIndeterminate}
            onChange={toggleSelectAll}
          />
          <span className={styles['visually-hidden']}>
            Sélectionner toutes les lignes
          </span>
          <div>{selectedNumber}</div>
        </div>
      )}

      <table
        className={classNames(styles['table'], {
          [styles['table-separate']]: variant === TableVariant.SEPARATE,
          [styles['table-collapse']]: variant === TableVariant.COLLAPSE,
        })}
      >
        <caption className={styles['table-caption-no-display']}>
          {title}
        </caption>
        <thead>
          <tr
            className={classNames(styles['table-header'], {
              [styles['table-header-sticky']]: isSticky,
            })}
          >
            {selectable && (
              <th scope="col" className={styles['table-header-th']}>
                <span className={styles['visually-hidden']}>Sélectionner</span>
              </th>
            )}
            {columns.map((col) => {
              if (col.headerHidden) {
                return null
              }
              const headerContent = col.header ?? col.label ?? ''

              return (
                <th
                  scope="col"
                  id={col.id}
                  colSpan={col.headerColSpan || 1}
                  key={`col-${col.id}`}
                  className={classNames(
                    styles.columnWidth,
                    styles['table-header-th'],
                    { [styles['table-header-sortable-th']]: col.sortable }
                  )}
                >
                  {col.sortable ? (
                    <SortColumn
                      onClick={() => sortTableColumn(col.id)}
                      sortingMode={
                        currentSortingColumn === col.id
                          ? currentSortingMode
                          : SortingMode.NONE
                      }
                    >
                      {headerContent}
                    </SortColumn>
                  ) : (
                    headerContent
                  )}
                </th>
              )
            })}
          </tr>
        </thead>

        <tbody>
          {isLoading &&
            Array.from({ length: 8 }).map((_, index) => (
              <tr key={`loading-row-${columns.length}-${index}`}>
                <td colSpan={columns.length + 1}>
                  <Skeleton height="7rem" width="100%" />
                </td>
              </tr>
            ))}

          {!sortedData.length && (
            <TableNoFilterResult
              colSpan={columns.length + (selectable ? 1 : 0)}
              message={noResult.message}
              subtitle={noResult.subtitle}
              resetMessage={noResult.resetMessage}
              resetFilters={noResult.onFilterReset}
            />
          )}

          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)
            const tableFullRowContent = getFullRowContent?.(row)

            return (
              <React.Fragment key={row.id}>
                <tr
                  data-testid="table-row"
                  className={classNames({
                    [styles['table-row']]: !tableFullRowContent,
                    [styles.selected]: isSelected,
                  })}
                >
                  {selectable && (
                    <td
                      className={classNames(styles['table-checkbox-cell'], {
                        [styles['table-separate-cell']]:
                          variant === TableVariant.SEPARATE,
                        [styles['table-collapse-cell']]:
                          variant === TableVariant.COLLAPSE,
                      })}
                    >
                      <Checkbox
                        label={row.name ?? `ligne ${row.id}`}
                        checked={isSelected}
                        onChange={() => toggleSelectRow(row)}
                        className={styles['table-checkbox-label']}
                        disabled={
                          isRowSelectable ? !isRowSelectable(row) : false
                        }
                      />
                      <span className={styles['visually-hidden']}>
                        Selectionner la ligne {row.name || row.id}
                      </span>
                    </td>
                  )}

                  {columns.map((col, index) => {
                    if (col.bodyHidden) {
                      return null
                    }
                    const value = col.render
                      ? col.render(row)
                      : getValue(row, col.ordererField)

                    return (
                      <td
                        className={classNames({
                          [styles['table-separate-cell']]:
                            variant === TableVariant.SEPARATE,
                          [styles['table-collapse-cell']]:
                            variant === TableVariant.COLLAPSE,
                        })}
                        key={`col-${col.id}-${index}`}
                        data-label={col.label}
                      >
                        {value}
                      </td>
                    )
                  })}
                </tr>
                {tableFullRowContent && (
                  <tr className={classNames(styles['table-row'])}>
                    <td colSpan={columns.length + (selectable ? 1 : 0)}>
                      <div className={styles['table-fullrow-content']}>
                        {tableFullRowContent}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
      {pagination && (
        <div className={styles['table-pagination']}>
          <Pagination
            currentPage={pagination.currentPage}
            pageCount={pagination.pageCount}
            onPageClick={pagination.onPageClick}
          />
        </div>
      )}
    </div>
  )
}
