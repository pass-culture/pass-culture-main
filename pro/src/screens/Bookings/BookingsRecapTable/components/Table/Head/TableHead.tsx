import React from 'react'
import type { HeaderGroup, TableInstance } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'

import styles from './TableHead.module.scss'

const IS_MULTI_SORT_ACTIVATED = false

export interface TableHeadProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  headerGroups: TableInstance<T>['headerGroups']
}

const TableHead = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  headerGroups,
}: TableHeadProps<T>) => {
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting()

  return (
    <thead className={styles['bookings-head']}>
      {headerGroups.map(headerGroup => (
        <tr key="header-group">
          {headerGroup.headers.map(
            (
              column: HeaderGroup<T> & {
                className?: string
              }
            ) => {
              const sortingMode =
                currentSortingColumn === column.id
                  ? currentSortingMode
                  : SortingMode.NONE

              return (
                <th className={column.className} key={column.id}>
                  {column.render('Header')}

                  {column.canSort ? (
                    <SortArrow
                      sortingMode={sortingMode}
                      onClick={() => {
                        const sortingMode = onColumnHeaderClick(column.id)

                        switch (sortingMode) {
                          case SortingMode.ASC:
                            return column.toggleSortBy(
                              false,
                              IS_MULTI_SORT_ACTIVATED
                            )
                          case SortingMode.DESC:
                            return column.toggleSortBy(
                              true,
                              IS_MULTI_SORT_ACTIVATED
                            )
                          default:
                            return column.toggleSortBy(
                              undefined,
                              IS_MULTI_SORT_ACTIVATED
                            )
                        }
                      }}
                    />
                  ) : (
                    ''
                  )}
                </th>
              )
            }
          )}
        </tr>
      ))}
    </thead>
  )
}

export default TableHead
