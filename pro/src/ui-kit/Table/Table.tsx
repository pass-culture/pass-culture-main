import classNames from 'classnames'
import React, { useEffect, useMemo, useState } from 'react'

import { SortingMode } from 'commons/hooks/useColumnSorting'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { Skeleton } from 'ui-kit/Skeleton/Skeleton'

import { SortColumn } from './SortColumn/SortColumn'
import styles from './Table.module.scss'
import { TableNoFilterResult } from './TableNoFilterResult/TableNoFilterResult'

export enum TableVariant {
  COLLAPSE = 'collapse',
  SEPARATE = 'separate',
}

type NoResultProps = {
  message: string
  resetFilter: () => void
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
}

type SortDirection = SortingMode.ASC | SortingMode.DESC | SortingMode.NONE

export interface TableProps<T extends { id: string | number }> {
  title?: string
  columns: Column<T>[]
  data: T[]
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
    return ordererField.split('.').reduce<any>((obj, key) => obj?.[key], row)
  }
  return (row as any)[ordererField]
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
  selectable = false,
  selectedNumber,
  selectedIds: controlledSelectedIds,
  className,
  isLoading,
  isSticky,
  variant,
  noResult,
  onSelectionChange,
  getFullRowContent,
  isRowSelectable,
}: TableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDirection>(SortingMode.NONE)
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(
    new Set(controlledSelectedIds || [])
  )

  useEffect(() => {
    if (controlledSelectedIds) {
      setSelectedIds(new Set(controlledSelectedIds))
    }
  }, [controlledSelectedIds])

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

    return [...data].sort((a, b) => {
      const va = getValue(a, col.ordererField)
      const vb = getValue(b, col.ordererField)
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
  }, [data, sortKey, sortDir, columns])

  const toggleSort = (id: string) => {
    if (sortKey === id) {
      setSortDir((prev) =>
        prev === SortingMode.ASC ? SortingMode.DESC : SortingMode.ASC
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
            Sélectionner toutes les lignes
          </span>

          <div>{selectedNumber}</div>
        </div>
      )}

      <table
        role="table"
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
              [styles['table-header']]: isSticky,
            })}
          >
            {selectable && (
              <th
                role="columnheader"
                scope="col"
                className={styles['table-header-th']}
              >
                <span className={styles['visually-hidden']}>Sélectionner</span>
              </th>
            )}
            {columns.map((col, index) => {
              if (col.headerHidden) {
                return null
              }
              return (
                <th
                  scope="col"
                  id={col.id}
                  colSpan={col.headerColSpan || 1}
                  key={`col-${index}`}
                  className={classNames(styles.columnWidth, {
                    [styles['table-header-th']]: !col.sortable,
                    [styles['table-header-sortable-th']]: col.sortable,
                  })}
                >
                  {col.sortable ? (
                    <SortColumn
                      onClick={() => toggleSort(col.id)}
                      sortingMode={sortDir}
                    >
                      {col.label}
                    </SortColumn>
                  ) : (
                    col.label
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

          {!sortedData.length && (
            <TableNoFilterResult
              colSpan={columns.length}
              message={noResult.message}
              resetFilters={noResult.resetFilter}
            />
          )}

          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)
            const tableFullRowContent = getFullRowContent?.(row)

            return (
              <React.Fragment key={row.id}>
                <tr
                  role="row"
                  className={classNames(styles['table-row'], {
                    [styles.selected]: isSelected,
                  })}
                >
                  {selectable && (
                    <td
                      className={classNames(
                        styles['table-checkbox-cell'],
                        styles['table-cell']
                      )}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Checkbox
                        label={
                          Object.prototype.hasOwnProperty.call(row, 'name')
                            ? (row as any).name
                            : `ligne ${row.id}`
                        }
                        checked={isSelected}
                        onChange={() => toggleSelectRow(row)}
                        className={styles['table-checkbox-label']}
                        disabled={
                          isRowSelectable ? !isRowSelectable(row) : false
                        }
                      />
                      <span className={styles['visually-hidden']}>
                        Selectionner la ligne {(row as any).name || row.id}
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
                        className={styles['table-cell']}
                        key={`col-${index}`}
                        data-label={col.label}
                      >
                        <div
                          className={classNames({
                            [styles['table-fullrow-wrapper']]:
                              tableFullRowContent,
                          })}
                        >
                          {value}
                        </div>
                        {col.id === columns[1].id && tableFullRowContent && (
                          <div className={styles['table-fullrow-content']}>
                            {tableFullRowContent}
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
