import classNames from 'classnames'
import React, { KeyboardEvent, useMemo, useState } from 'react'

import { SortingMode } from 'commons/hooks/useColumnSorting'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { Skeleton } from 'ui-kit/Skeleton/Skeleton'

import styles from './ResponsiveTable.module.scss'

export interface Column<T> {
  id: string
  label: string
  sortable?: boolean
  accessor?: keyof T | ((row: T) => React.ReactNode)
  render?: (row: T) => React.ReactNode
  width?: string
  headerColSpan?: number
  bodyHidden?: boolean
  headerHidden?: boolean
  isRowSelectable?: (row: T) => boolean
}

type SortDirection = SortingMode.ASC | SortingMode.DESC | SortingMode.NONE

export interface ResponsiveTableProps<T extends { id: string | number }> {
  title?: string
  columns: Column<T>[]
  data: T[]
  selectable?: boolean
  onSelectionChange?: (rows: T[]) => void
  getRowLink?: (row: T) => string | undefined | null
  getExpandedContent?: (row: T) => React.ReactNode | null
  hover?: boolean
  className?: string
  isRowSelectable?: (row: T) => boolean
  isLoading: boolean
}

function getValue<T>(
  row: T,
  accessor?: keyof T | string | ((r: T) => unknown)
) {
  if (!accessor) {
    return undefined
  }
  if (typeof accessor === 'function') {
    return accessor(row)
  }
  if (typeof accessor === 'string') {
    return accessor.split('.').reduce<any>((obj, key) => obj?.[key], row)
  }
  return (row as any)[accessor]
}

export function ResponsiveTable<
  T extends {
    name?: string
    id: string | number
  },
>({
  title = 'Tableau de données',
  columns,
  data,
  selectable = false,
  onSelectionChange,
  getRowLink,
  getExpandedContent,
  hover = true,
  className,
  isRowSelectable,
  isLoading,
}: ResponsiveTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDirection>(SortingMode.NONE)
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(
    new Set()
  )

  const selectableRows = useMemo(
    () => (isRowSelectable ? data.filter(isRowSelectable) : data),
    [data, isRowSelectable]
  )

  const sortedData = useMemo(() => {
    if (!sortKey) {
      return data
    }
    const col = columns.find((c) => c.id === sortKey)
    if (!col) {
      return data
    }

    const copy = [...data]
    copy.sort((a, b) => {
      const va = getValue(a, col.accessor)
      const vb = getValue(b, col.accessor)
      if (va === vb) {
        return 0
      }
      return (va as any) < (vb as any)
        ? sortDir === SortingMode.ASC
          ? -1
          : 1
        : sortDir === SortingMode.ASC
          ? 1
          : -1
    })
    return copy
  }, [data, sortKey, sortDir, columns])

  const toggleSort = (id: string, sortable?: boolean) => {
    if (!sortable) {
      return
    }
    if (sortKey === id) {
      setSortDir((d) =>
        d === SortingMode.ASC ? SortingMode.DESC : SortingMode.ASC
      )
    } else {
      setSortKey(id)
      setSortDir(SortingMode.ASC)
    }
  }

  const toggleSelectAll = () => {
    if (selectedIds.size === selectableRows.length) {
      setSelectedIds(new Set())
      onSelectionChange?.([])
    } else {
      const all = new Set(selectableRows.map((r) => r.id))
      setSelectedIds(all)
      onSelectionChange?.(selectableRows)
    }
  }

  const toggleSelectRow = (row: T) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(row.id)) {
      newSet.delete(row.id)
    } else {
      newSet.add(row.id)
    }
    setSelectedIds(newSet)
    onSelectionChange?.(data.filter((r) => newSet.has(r.id)))
  }

  const handleRowNavigation = (row: T) => {
    const href = getRowLink?.(row)
    if (!href) {
      return
    }
    window.location.assign(href)
  }

  const handleRowKeyDown =
    (row: T) => (e: KeyboardEvent<HTMLTableRowElement>) => {
      if (!getRowLink) {
        return
      }
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleRowNavigation(row)
      }
    }

  return (
    <div
      role="region"
      aria-label={title}
      className={classNames(styles.wrapper, className)}
      tabIndex={0}
    >
      {selectable && (
        <div className={styles['table-select-all']}>
          <Checkbox
            label={
              selectedIds.size < selectableRows.length
                ? 'Tout sélectionner'
                : 'Tout désélectionner'
            }
            checked={
              selectedIds.size === selectableRows.length &&
              selectableRows.length > 0
            }
            onChange={toggleSelectAll}
            indeterminate={
              selectedIds.size > 0 && selectedIds.size < selectableRows.length
            }
          />
          <span className={styles['visually-hidden']}>
            Sélectionner toutes les offres
          </span>
        </div>
      )}

      <table role="table" aria-label={title} className={styles.table}>
        <caption className={styles['visually-hidden']}>{title}</caption>
        <thead>
          <tr className={styles['table-header']}>
            {selectable && (
              <th scope="col" className={styles['table-header-th']}>
                <span className={styles['visually-hidden']}>
                  Sélectionner les lignes
                </span>
              </th>
            )}

            {columns.map((col) => {
              if (col.headerHidden) {
                return null
              }
              return (
                <th
                  id={col.id}
                  scope="col"
                  colSpan={col.headerColSpan || 1}
                  key={col.id}
                  className={classNames(
                    styles.columnWidth,
                    styles['table-header-th'],
                    {
                      [styles.sortable]: col.sortable,
                    }
                  )}
                  style={{ width: col.width }}
                >
                  {col.label}
                  {col.sortable && (
                    <SortArrow
                      onClick={() => toggleSort(col.id, col.sortable)}
                      sortingMode={sortDir}
                    />
                  )}
                </th>
              )
            })}
          </tr>
        </thead>

        <tbody role="rowgroup">
          {isLoading &&
            Array.from({ length: 8 }).map((_, index) => (
              <tr key={`loading-row-${index}`}>
                <td colSpan={columns.length + 1}>
                  <Skeleton height="7rem" width="100%" margin="0" />
                </td>
              </tr>
            ))}

          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)
            const expandedContent = getExpandedContent?.(row)
            const hasNavigation = Boolean(getRowLink?.(row))

            return (
              <React.Fragment key={row.id}>
                <tr
                  role="row"
                  tabIndex={hasNavigation ? 0 : undefined}
                  onClick={() => handleRowNavigation(row)}
                  onKeyDown={handleRowKeyDown(row)}
                  className={classNames(styles.row, {
                    [styles.hover]: hover && hasNavigation,
                    [styles.selected]: isSelected,
                    [styles.clickable]: hasNavigation,
                    [styles['interactive-row']]: hasNavigation,
                  })}
                >
                  {selectable && (
                    <td
                      className={classNames(
                        styles.checkboxCell,
                        styles['table-cell']
                      )}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Checkbox
                        label={
                          Object.prototype.hasOwnProperty.call(row, 'name')
                            ? (row as any).name
                            : `Offre ${row.id}`
                        }
                        checked={isSelected}
                        onChange={() => toggleSelectRow(row)}
                        className={styles['checkbox-label']}
                        disabled={
                          isRowSelectable ? !isRowSelectable(row) : false
                        }
                      />
                      <span className={styles['visually-hidden']}>
                        Selectionner l’offre {(row as any).name || row.id}
                      </span>
                    </td>
                  )}

                  {columns.map((col) => {
                    if (col.bodyHidden) {
                      return null
                    }
                    const value = col.render
                      ? col.render(row)
                      : getValue(row, col.accessor)
                    return (
                      <td
                        className={styles['table-cell']}
                        key={col.id}
                        data-label={col.label}
                        onClick={(e) => {
                          if (
                            (e.target as HTMLElement).closest(
                              'button, a, input, [data-stop-propagation]'
                            )
                          ) {
                            e.stopPropagation()
                          }
                        }}
                      >
                        <div
                          className={classNames({
                            [styles['cell-main']]: expandedContent,
                          })}
                        >
                          {value}
                        </div>
                        {col.id === columns[1].id && expandedContent && (
                          <div className={styles['expanded-inside']}>
                            {expandedContent}
                          </div>
                        )}
                      </td>
                    )
                  })}
                </tr>
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
