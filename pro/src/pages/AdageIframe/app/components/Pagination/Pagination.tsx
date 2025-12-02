import { useEffect } from 'react'
import { usePagination } from 'react-instantsearch'
import { useParams } from 'react-router'

import { PaginationType } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setAdagePageSaved } from '@/commons/store/adageFilter/reducer'
import { adagePageSavedSelector } from '@/commons/store/adageFilter/selectors'
import { Pagination } from '@/design-system/Pagination/Pagination'

interface CustomPaginationProps {
  queryId?: string
  onPageChange?(): void
}

export const CustomPagination = ({
  queryId,
  onPageChange,
}: CustomPaginationProps) => {
  const dispatch = useAppDispatch()
  const adagePageSavedFromSelector = useAppSelector(adagePageSavedSelector)

  const { currentRefinement, nbPages, refine } = usePagination()
  const { siret, venueId } = useParams<{
    siret: string
    venueId: string
  }>()

  const logPagination = async (type: PaginationType) => {
    await apiAdage.logSearchShowMore({
      iframeFrom: location.pathname,
      source: siret || venueId ? 'partnersMap' : 'homepage',
      queryId: queryId,
      type,
    })
  }

  useEffect(() => {
    if (currentRefinement !== adagePageSavedFromSelector) {
      refine(adagePageSavedFromSelector)
    }
  }, [refine, currentRefinement, adagePageSavedFromSelector])

  return (
    <Pagination
      currentPage={currentRefinement + 1}
      pageCount={nbPages}
      onPageClick={(newPage) => {
        dispatch(setAdagePageSaved(newPage - 1))
        onPageChange?.()

        // Clicked page is the immediate previous page
        if (newPage === currentRefinement) {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          logPagination(PaginationType.PREVIOUS)
        }
        // Clicked page is the immediate next page
        else if (newPage === currentRefinement + 2) {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          logPagination(PaginationType.NEXT)
        }
      }}
    />
  )
}
