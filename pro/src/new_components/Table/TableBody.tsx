import React from 'react'

interface ITableBody {
  page: any,
  prepareRow: () => void,
  tableBodyProps: any,
}

const TableBody = ({
  page = [{ cells: [{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"}]},{ cells: [{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"},{coucou: "coucou"}]}],
  }: ITableBody) => {
  return (
    <tbody
      className="bookings-body"
    >
    {page.map((row:any) => {
      return (
        <tr
          key={row.index}
        >
          {row.cells.map((cell:any) => {
            return (
              <td
                key={cell.id}
              >
                {cell.coucou}
              </td>
            )
          })}
        </tr>
      )
    })}
    </tbody>
  )
}

export default TableBody
