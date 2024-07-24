import { useEffect } from 'react'
import { usePagination } from 'react-instantsearch'
import { useDispatch, useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'

import { PaginationType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { setAdagePageSaved } from 'store/adageFilter/reducer'
import { adagePageSavedSelector } from 'store/adageFilter/selectors'
import { Pagination } from 'ui-kit/Pagination/Pagination'

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
      onNextPageClick={() => {
        dispatch(setAdagePageSaved(currentRefinement + 1))
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        logPagination(PaginationType.NEXT)
      }}
      onPreviousPageClick={() => {
        dispatch(setAdagePageSaved(currentRefinement - 1))
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        logPagination(PaginationType.PREVIOUS)
      }}
      pageCount={nbPages}
    />
  )
}
