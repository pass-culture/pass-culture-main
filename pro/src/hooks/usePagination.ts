import { useState, useCallback } from 'react'

export const usePagination = <T>(items: T[], itemsPerPage: number) => {
  const [page, setPage] = useState(1)

  const previousPage = useCallback(() => setPage(page => page - 1), [])
  const nextPage = useCallback(() => setPage(page => page + 1), [])

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
