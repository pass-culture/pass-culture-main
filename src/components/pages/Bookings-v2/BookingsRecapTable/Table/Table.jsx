import React from 'react'
import { useTable, usePagination } from 'react-table'

function Table({columns, data}) {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    nextPage,
    previousPage,
    state: { pageIndex },
  } = useTable(
    {
      columns,
      data,
      initialState: { pageIndex: 0, pageSize: 5 },
    },
    usePagination
  )

  return (
    <div>
      <table
        className="bookings-table"
        {...getTableProps()}
      >
        <thead>
        {headerGroups.map(headerGroup => (
          <tr
            key={headerGroup.id}
            {...headerGroup.getHeaderGroupProps()}
          >
            {headerGroup.headers.map(column => (
              <th
                key={column.id}
                {...column.getHeaderProps()}
              >
                {column.render('headerTitle')}
              </th>
            ))}
          </tr>
        ))}
        </thead>
        <tbody {...getTableBodyProps()}>
        {page.map(row => {
          prepareRow(row)
          return (
            <tr
              key={row.id}
              {...row.getRowProps()}
            >
              {row.cells.map(cell => {
                return (
                  <td
                    key={cell.id}
                    {...cell.getCellProps({ className: cell.column.className })}
                  >
                    {cell.render('Cell')}
                  </td>
                )
              })}
            </tr>
          )
        })}
        </tbody>
      </table>


    </div>
  )
}

export default Table
