import { useEffect } from 'react'
import { usePagination } from 'react-instantsearch'
import { useDispatch, useSelector } from 'react-redux'
import { useParams } from 'react-router'

import { PaginationType } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { setAdagePageSaved } from '@/commons/store/adageFilter/reducer'
import { adagePageSavedSelector } from '@/commons/store/adageFilter/selectors'
import { Pagination } from '@/design-system/Pagination/Pagination'

interface CustomPaginationProps {
  queryId?: string
}

export const CustomPagination = ({ queryId }: CustomPaginationProps) => {
  const dispatch = useDispatch()
  const adagePageSavedFromSelector = useSelector(adagePageSavedSelector)

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
