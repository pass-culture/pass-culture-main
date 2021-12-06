import React, {
  useCallback,
  useEffect,
  useState,
} from 'react'

import styles from './Table.module.scss'
import TableBody from './TableBody/TableBody'
import TableHead from './TableHead/TableHead'



interface ITableProps {
  rowsTitleOptions: [
    {
      title: string,
      sortBy: string,
      selfDirection: string
    }
  ],
  rows: []
}

const IS_ASCENDENT = 'asc'
const IS_DESCENDENT = 'desc'
const DEFAULT_DIRECTION = IS_ASCENDENT

const Table = ({ rows, rowsTitleOptions }: ITableProps): JSX.Element => {

  const [direction, setDirection] = useState(DEFAULT_DIRECTION)
  const [selectedTitle, setSelectedTitle] = useState('date')
  const [sortedData, setSortedData] = useState([...rows])

  const changeDirection = (directionToChange:string) => directionToChange === IS_ASCENDENT ? IS_DESCENDENT : IS_ASCENDENT
  const sortBy = (fieldToSort:string, sortDirection:string) => {

    const newSortedData = rows.sort((columnA, columnB) => {
      if (columnA[fieldToSort] < columnB[fieldToSort]) return sortDirection === IS_ASCENDENT ? -1 : 1
      if (columnA[fieldToSort] > columnB[fieldToSort]) return sortDirection === IS_ASCENDENT ? 1 : -1
      return 0
    })
    setSortedData(newSortedData)
  }

  const targetedTitle = useCallback((newSelectedTitle) => {

    const newDirection = newSelectedTitle === selectedTitle ? changeDirection(direction) : DEFAULT_DIRECTION

    sortBy(newSelectedTitle,newDirection)
    setSelectedTitle(newSelectedTitle)
    setDirection(newDirection)
  }, [selectedTitle, direction])

  useEffect(() => {
    sortBy(selectedTitle, direction)
  }, [rows])

  return (
    <table className={styles["table"]}>
      <TableHead
        rowTitlesOptions={rowsTitleOptions}
        sortBy={targetedTitle}
      />
      <TableBody
        rows={sortedData}
      />
    </table>
  )
}

export default Table
