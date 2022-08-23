import React, { KeyboardEvent } from 'react'
import type { HeaderGroup, TableInstance } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import Icon from 'components/layout/Icon'

const IS_MULTI_SORT_ACTIVATED = false

const handleOnKeyDown =
  <T extends BookingRecapResponseModel | CollectiveBookingResponseModel>(
    column: HeaderGroup<T>,
    selector?: boolean
  ) =>
  (event: KeyboardEvent<HTMLImageElement>) => {
    const enterKeyHasBeenPressed = event.key === 'Enter'
    if (enterKeyHasBeenPressed) {
      column.toggleSortBy(selector, IS_MULTI_SORT_ACTIVATED)
    }
  }

interface ITableHeadProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  headerGroups: TableInstance<T>['headerGroups']
}

const TableHead = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  headerGroups,
}: ITableHeadProps<T>) => {
  return (
    <thead className="bookings-head">
      {headerGroups.map(headerGroup => (
        <tr key="header-group">
          {headerGroup.headers.map(
            (
              column: HeaderGroup<T> & {
                className?: string
              }
            ) => (
              <th
                {...column.getHeaderProps(column.getSortByToggleProps())}
                className={column.className}
                key={column.id}
              >
                {column.render('Header')}
                {column.canSort ? (
                  <span className="sorting-icons">
                    {column.isSorted ? (
                      column.isSortedDesc ? (
                        <Icon
                          onKeyDown={handleOnKeyDown(column)}
                          role="button"
                          svg="ico-arrow-up-r"
                          tabIndex={0}
                        />
                      ) : (
                        <Icon
                          onKeyDown={handleOnKeyDown(column, true)}
                          role="button"
                          svg="ico-arrow-down-r"
                          tabIndex={0}
                        />
                      )
                    ) : (
                      <Icon
                        onKeyDown={handleOnKeyDown(column, false)}
                        role="button"
                        svg="ico-unfold"
                        tabIndex={0}
                      />
                    )}
                  </span>
                ) : (
                  ''
                )}
              </th>
            )
          )}
        </tr>
      ))}
    </thead>
  )
}

export default TableHead
