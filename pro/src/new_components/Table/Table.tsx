import React from 'react'

import TableBody from './TableBody'
import TableHead from './TableHeader'


interface ITable {
  headerGroups: [],
  page: [],
  prepareRow: () => void,
}


const Table = ({
  page,
  prepareRow,
}: ITable) => {
  const headerGroups = [{
    "headers": [
      {
        "id": 1,
        "headerTitle": "Nom de l'offre",
        "className": "column-offer-name",
        "defaultCanSort": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 0,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": true,
        "isSorted": false,
        "sortedIndex": -1
      },
      {
        "id": 2,
        "headerTitle": "",
        "className": "column-booking-duo",
        "disableSortBy": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortType": "alphanumeric",
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 150,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": false,
        "isSorted": false,
        "sortedIndex": -1
      },
      {
        "id": 3,
        "headerTitle": "Bénéficiaire",
        "className": "column-beneficiary",
        "defaultCanSort": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 300,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": true,
        "isSorted": false,
        "sortedIndex": -1
      },
      {
        "id": 4,
        "headerTitle": "Réservation",
        "className": "column-booking-date",
        "defaultCanSort": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 450,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": true,
        "isSorted": false,
        "sortedIndex": -1
      },
      {
        "id": 5,
        "headerTitle": "Contremarque",
        "className": "column-booking-token",
        "disableSortBy": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortType": "alphanumeric",
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 600,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": false,
        "isSorted": false,
        "sortedIndex": -1
      },
      {
        "id": 6,
        "className": "column-booking-status",
        "disableSortBy": true,
        "depth": 0,
        "width": 150,
        "minWidth": 0,
        "maxWidth": 9007199254740991,
        "sortType": "alphanumeric",
        "sortDescFirst": false,
        "canResize": true,
        "originalWidth": 150,
        "isVisible": true,
        "totalVisibleHeaderCount": 1,
        "totalLeft": 750,
        "totalMinWidth": 0,
        "totalWidth": 150,
        "totalMaxWidth": 9007199254740991,
        "totalFlexWidth": 150,
        "canSort": false,
        "isSorted": false,
        "sortedIndex": -1
      }
    ]
  }]
  return (
    <div className="bookings-table-wrapper">
      <table
        className="bookings-table"
      >
        <TableHead headerGroups={headerGroups} />
        <TableBody
          page={page}
          prepareRow={prepareRow}
          tableBodyProps={()=>{}}
        />
      </table>
    </div>
  )
}

export default Table
