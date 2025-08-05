import { useState } from 'react'

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
