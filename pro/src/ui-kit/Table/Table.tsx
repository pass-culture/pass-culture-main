import classNames from 'classnames'
import React, { useMemo, useState } from 'react'

import { SortingMode, useColumnSorting } from 'commons/hooks/useColumnSorting'
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
  onFilterReset: () => void
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

interface TableProps<T extends { id: string | number }> {
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
    onSelectionChange?.(data.filter((r) => newSelectedIds.has(r.id)))
  }

  function sortTableColumn(col: unknown) {
    onColumnHeaderClick(col)
  }

  const selectableRows = useMemo(
    () => (isRowSelectable ? data.filter(isRowSelectable) : data),
    [data, isRowSelectable]
  )

  const toggleSelectAll = () => {
    if (selectedIds.size === selectableRows.length) {
      updateSelectedIds(new Set())
    } else {
      updateSelectedIds(new Set(selectableRows.map((r) => r.id)))
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

    return [...data].sort((a, b) => {
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
  }, [data, currentSortingColumn, currentSortingMode, columns])

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
              <th scope="col" className={styles['table-header-th']}>
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
                  className={classNames(
                    styles.columnWidth,
                    styles['table-header-th'],
                    {
                      [styles['table-header-sortable-th']]: col.sortable,
                    }
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

        <tbody>
          {isLoading &&
            Array.from({ length: 8 }).map((_, index) => (
              <tr key={`loading-row-${index}`}>
                <td colSpan={columns.length + 1}>
                  <Skeleton height="7rem" width="100%" />
                </td>
              </tr>
            ))}

          {!sortedData.length && (
            <TableNoFilterResult
              colSpan={columns.length + (selectable ? 1 : 0)}
              message={noResult.message}
              resetFilters={noResult.onFilterReset}
            />
          )}

          {sortedData.map((row) => {
            const isSelected = selectedIds.has(row.id)
            const tableFullRowContent = getFullRowContent?.(row)

            return (
              <React.Fragment key={row.id}>
                <tr
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
                          row.hasOwnProperty.call(row, 'name')
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
                        {value}
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
