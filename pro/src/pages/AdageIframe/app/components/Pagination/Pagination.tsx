import { usePagination } from 'react-instantsearch'
import { useParams } from 'react-router-dom'

import { PaginationType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { Pagination } from 'ui-kit/Pagination/Pagination'

interface CustomPaginationProps {
  queryId?: string
}

export const CustomPagination = ({ queryId }: CustomPaginationProps) => {
  const { currentRefinement, nbPages, refine } = usePagination()
  const { siret, venueId } = useParams<{
    siret: string
    venueId: string
  }>()

  console.log('lalala ?')

  const logPagination = async (type: PaginationType) => {
    await apiAdage.logSearchShowMore({
      iframeFrom: location.pathname,
      source: siret || venueId ? 'partnersMap' : 'homepage',
      queryId: queryId,
      type,
    })
  }

  return (
    <Pagination
      currentPage={currentRefinement + 1}
      onNextPageClick={() => {
        refine(currentRefinement + 1)
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        logPagination(PaginationType.NEXT)
      }}
      onPreviousPageClick={() => {
        refine(currentRefinement - 1)
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        logPagination(PaginationType.PREVIOUS)
      }}
      pageCount={nbPages}
    />
  )
}
