import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

export const usePagination = <T>(
  items: T[],
  itemsPerPage: number,
  pageFromFilter?: number
) => {
  const [page, setPage] = useState(pageFromFilter ?? 1)

  const previousPage = () => setPage((page) => page - 1)
  const nextPage = () => setPage((page) => page + 1)

  const currentPageItems = items.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  )
  const pageCount = Math.ceil(items.length / itemsPerPage)

  return {
    page,
    setPage,
    previousPage,
    nextPage,
    currentPageItems,
    pageCount,
  }
}

// FIX ME: 27/10/2023
// we duplicate this hook for now since bookings pages also used it
// once we have adapted bookings pagination we can delete the old one
// this is planned in PC-25444
export const usePaginationWithSearchParams = (
  itemsPerPage: number,
  totalCount: number = 0
) => {
  const [searchParams, setSearchParams] = useSearchParams()
  const page = Number(searchParams.get('page')) || 1

  const pageCount = Math.ceil(totalCount / itemsPerPage)

  const previousPage = () => {
    searchParams.set('page', (page - 1).toString())
    setSearchParams(searchParams)
  }
  const nextPage = () => {
    searchParams.set('page', (page + 1).toString())
    setSearchParams(searchParams)
  }
  const firstPage = () => {
    searchParams.set('page', '1')
    setSearchParams(searchParams)
  }
  const lastPage = () => {
    searchParams.set('page', pageCount.toString())
    setSearchParams(searchParams)
  }

  return {
    page,
    previousPage,
    nextPage,
    firstPage,
    lastPage,
    pageCount,
  }
}
