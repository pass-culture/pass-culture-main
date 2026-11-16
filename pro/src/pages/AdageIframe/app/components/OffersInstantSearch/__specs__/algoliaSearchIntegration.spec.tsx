import { render, waitFor } from '@testing-library/react'
import { liteClient } from 'algoliasearch/lite'
import { Configure, InstantSearch } from 'react-instantsearch'

import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'

import { AlgoliaSearchErrorListener } from '../AlgoliaSearchErrorListener'
import { monitorAlgoliaSearch } from '../algoliaSearchClient'

const snackBarError = vi.fn()
const snackBar = { error: snackBarError }

vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => snackBar,
}))

describe('Algolia search error handling', () => {
  it('reports the original search failure and informs the user while mounted', async () => {
    const client = liteClient('app', 'key')
    const error = Object.assign(new Error('Algolia unavailable'), {
      status: 503,
    })
    vi.spyOn(client, 'search').mockRejectedValue(error)

    render(
      <InstantSearch
        indexName="offers"
        searchClient={monitorAlgoliaSearch(client)}
      >
        <Configure hitsPerPage={8} />
        <AlgoliaSearchErrorListener />
      </InstantSearch>
    )

    await waitFor(() => {
      expect(handleUnexpectedError).toHaveBeenCalledExactlyOnceWith(error, {
        isSilent: true,
        context: { operation: 'adage-offers-search', status: 503 },
      })
      expect(snackBarError).toHaveBeenCalledExactlyOnceWith(
        'Une erreur est survenue lors de la recherche. Veuillez réessayer.'
      )
    })
  })
})
