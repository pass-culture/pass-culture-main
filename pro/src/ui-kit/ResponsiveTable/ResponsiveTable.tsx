import classNames from 'classnames'
import React, { useMemo, useState } from 'react'

import { SortingMode } from 'commons/hooks/useColumnSorting'
import { NoResults } from 'components/NoResults/NoResults'
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
  isRowSelectable?: (row: T) => boolean
}

type SortDirection = SortingMode.ASC | SortingMode.DESC | SortingMode.NONE

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
  isRowSelectable?: (row: T) => boolean
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
    // support “a.b.c” paths
    return accessor.split('.').reduce<any>((obj, key) => obj?.[key], row)
  }
  return (row as any)[accessor]
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
  isRowSelectable,
}: ResponsiveTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDirection>(SortingMode.NONE)
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(
    new Set()
  )

  // ---- sorting -------------------------------------------------
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

  // rows that MAY be selected (respect the isRowSelectable guard)
  const selectableRows = useMemo(
    () => (isRowSelectable ? data.filter(isRowSelectable) : data),
    [data, isRowSelectable]
  )

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

  if (!hasOffers && hasFiltersOrNameSearch) {
    return <NoResults resetFilters={resetFilters} />
  }

  return (
    <div className={classNames(styles.wrapper, className)} tabIndex={0}>
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
      <table role="table" className={styles['table']}>
        <caption>Titre du tableau</caption>
        <thead>
          <tr className={styles['table-header']}>
            {selectable && <th className={styles['table-header-th']}></th>}
            {columns.map((col) => {
              if (col.headerHidden) {
                // Header‑only column: skip rendering any <td>
                return
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
                    ></SortArrow>
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody role="rowgroup">
          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)

            return (
              <React.Fragment key={row.id}>
                <tr
                  role="row"
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
                        disabled={
                          isRowSelectable ? !isRowSelectable(row) : false
                        }
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
                      : getValue(row, col.accessor)

                    return (
                      <td
                        className={styles['table-cell']}
                        key={col.id}
                        data-label={col.label}
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
