import { render } from '@testing-library/react'
import { useInstantSearch } from 'react-instantsearch'

import { AlgoliaSearchErrorListener } from '../AlgoliaSearchErrorListener'

const snackBarError = vi.fn()
const snackBar = { error: snackBarError }
const searchState = vi.hoisted(() => ({
  status: 'idle',
  error: undefined as Error | undefined,
}))

vi.mock('react-instantsearch', () => ({
  useInstantSearch: vi.fn(() => searchState),
}))

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => snackBar,
}))

describe('AlgoliaSearchErrorListener', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    searchState.status = 'idle'
    searchState.error = undefined
  })

  it('catches InstantSearch errors and informs the user once per error', () => {
    const { rerender } = render(<AlgoliaSearchErrorListener />)
    expect(useInstantSearch).toHaveBeenCalledWith({ catchError: true })
    expect(snackBarError).not.toHaveBeenCalled()

    searchState.status = 'error'
    searchState.error = new Error('Search failed')
    rerender(<AlgoliaSearchErrorListener />)
    rerender(<AlgoliaSearchErrorListener />)

    expect(snackBarError).toHaveBeenCalledExactlyOnceWith(
      'Une erreur est survenue lors de la recherche. Veuillez réessayer.'
    )
  })
})
