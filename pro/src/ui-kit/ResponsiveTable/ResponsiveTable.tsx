import classNames from 'classnames'
import React, { useMemo, useState } from 'react'

import { SortingMode } from 'commons/hooks/useColumnSorting'
import { NoResults } from 'components/NoResults/NoResults'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Checkbox } from 'design-system/Checkbox/Checkbox'

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
}

type SortDirection = 'asc' | 'desc'

interface ResponsiveTableProps<T extends { id: string | number }> {
  columns: Column<T>[]
  data: T[]
  /** show row‑selection checkboxes */
  selectable?: boolean
  /** callback fired whenever the set of selected rows changes */
  onSelectionChange?: (rows: T[]) => void
  /** return link (href) for a row – row becomes clickable */
  getRowLink?: (row: T) => string
  /** return expanded area content for a row (optional) */
  getExpandedContent?: (row: T) => React.ReactNode | null
  /** enable row hover styling (default true) */
  hover?: boolean
  hasFiltersOrNameSearch?: boolean
  hasOffers?: boolean
  resetFilters: () => void
  className?: string
}

export function ResponsiveTable<
  T extends {
    name: string
    id: string | number
  },
>({
  columns,
  data,
  selectable = false,
  onSelectionChange,
  getExpandedContent,
  hover = true,
  hasFiltersOrNameSearch = false,
  hasOffers = false,
  resetFilters,
  className,
}: ResponsiveTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDirection>(SortingMode.ASC)
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(
    new Set()
  )

  // sort handler
  const sortedData = useMemo(() => {
    if (!sortKey) {
      return data
    }
    const col = columns.find((c) => c.id === sortKey)
    if (!col) {
      return data
    }

    const accessor = col.accessor as keyof T | ((row: T) => any)
    const copy = [...data]
    copy.sort((a, b) => {
      const va =
        typeof accessor === 'function' ? accessor(a) : (a as any)[accessor]
      const vb =
        typeof accessor === 'function' ? accessor(b) : (b as any)[accessor]
      if (va < vb) {
        return sortDir === SortingMode.ASC ? -1 : 1
      }
      if (va > vb) {
        return sortDir === SortingMode.ASC ? 1 : -1
      }
      return 0
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
    if (selectedIds.size === data.length) {
      setSelectedIds(new Set())
      onSelectionChange?.([])
    } else {
      const all = new Set(data.map((r) => r.id))
      setSelectedIds(all)
      onSelectionChange?.(data)
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

  if (!hasOffers && hasFiltersOrNameSearch) {
    return <NoResults resetFilters={resetFilters} />
  }

  return (
    <div className={classNames(styles.wrapper, className)}>
      {selectable && (
        <div className={styles['table-select-all']}>
          <Checkbox
            label={
              selectedIds.size < data.length
                ? 'Tout sélectionner'
                : 'Tout désélectionner'
            }
            checked={selectedIds.size === data.length && data.length > 0}
            onChange={toggleSelectAll}
            indeterminate={
              selectedIds.size > 0 && selectedIds.size < data.length
            }
          />
          <span className={styles['visually-hidden']}>
            Sélectionner toutes les offres
          </span>
        </div>
      )}
      <table role="table" className={styles['table']}>
        <thead role="rowgroup">
          <tr role="row" className={styles['table-header']}>
            {selectable && <th className={styles['table-header-th']}></th>}
            {columns.map((col) => {
              if (col.headerHidden) {
                // Header‑only column: skip rendering any <td>
                return
              }
              return (
                <th
                  id={col.id}
                  colSpan={col.headerColSpan || 1}
                  role="columnheader"
                  key={col.id}
                  className={classNames(
                    styles.columnWidth,
                    styles['table-header-th'],
                    {
                      [styles.sortable]: col.sortable,
                    }
                  )}
                  onClick={() => toggleSort(col.id, col.sortable)}
                >
                  {col.label}
                  {sortKey === col.id && (
                    <SortArrow
                      onClick={() => toggleSort(col.id, col.sortable)}
                      sortingMode={
                        sortDir === SortingMode.ASC
                          ? SortingMode.ASC
                          : SortingMode.DESC
                      }
                    ></SortArrow>
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)

            return (
              <React.Fragment key={row.id}>
                <tr
                  className={classNames(styles.row, {
                    [styles.hover]: hover,
                    [styles.selected]: isSelected,
                  })}
                >
                  {selectable && (
                    <td
                      className={styles.checkboxCell}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Checkbox
                        label={row.name || `Offre ${row.id}`}
                        checked={isSelected}
                        onChange={() => toggleSelectRow(row)}
                        className={styles['checkbox-label']}
                      />
                      <span className={styles['visually-hidden']}>
                        Selectionner l’offre {row.name}
                      </span>
                    </td>
                  )}
                  {columns.map((col) => {
                    if (col.bodyHidden) {
                      // Header‑only column: skip rendering any <td>
                      return
                    }
                    const value = col.render
                      ? col.render(row)
                      : typeof col.accessor === 'function'
                        ? col.accessor(row)
                        : (row as any)[col.accessor as keyof T]
                    return (
                      <td
                        key={col.id}
                        data-label={col.label}
                        headers={`row-${value.id} ${getCellsDefinition().CHECKBOX.id}`}
                      >
                        {value}
                      </td>
                    )
                  })}
                </tr>

                {getExpandedContent && (
                  <tr className={styles.expandedRow}>
                    <td colSpan={(selectable ? 1 : 0) + columns.length}>
                      {getExpandedContent(row)}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
