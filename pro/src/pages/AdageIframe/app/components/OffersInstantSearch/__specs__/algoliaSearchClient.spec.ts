import { liteClient } from 'algoliasearch/lite'

import { isReportedAlgoliaWrapper } from '@/commons/errors/algoliaSearchErrors'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'

import { monitorAlgoliaSearch } from '../algoliaSearchClient'

vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))

describe('monitorAlgoliaSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('preserves successful results and request arguments', async () => {
    const client = liteClient('app', 'key')
    const response = { results: [] }
    const search = vi.spyOn(client, 'search').mockResolvedValue(response)
    const monitored = monitorAlgoliaSearch(client)
    const request = { requests: [] }

    await expect(monitored.search(request)).resolves.toBe(response)
    expect(search).toHaveBeenCalledWith(request)
    expect(handleUnexpectedError).not.toHaveBeenCalled()
  })

  it('reports the original error and rethrows it when the request fails', async () => {
    const client = liteClient('app', 'key')
    const error = Object.assign(new Error('Algolia unavailable'), {
      status: 503,
    })
    vi.spyOn(client, 'search').mockRejectedValue(error)
    const monitored = monitorAlgoliaSearch(client)

    await expect(monitored.search({ requests: [] })).rejects.toBe(error)
    expect(handleUnexpectedError).toHaveBeenCalledExactlyOnceWith(error, {
      isSilent: true,
      context: { operation: 'adage-offers-search', status: 503 },
    })

    const wrapper = Object.assign(
      new Error('Uncaught, unspecified "error" event. ([object Object])'),
      { context: { error } }
    )
    expect(isReportedAlgoliaWrapper(wrapper)).toBe(true)
  })

  it('reports a rejection even if it happens after the caller has moved on', async () => {
    const client = liteClient('app', 'key')
    let rejectSearch: (error: Error) => void = () => {
      throw new Error('Search was not started')
    }
    vi.spyOn(client, 'search').mockImplementation(
      () =>
        new Promise((_, reject) => {
          rejectSearch = reject
        })
    )
    const monitored = monitorAlgoliaSearch(client)
    const result = monitored.search({ requests: [] })
    const error = new Error('Late failure')

    rejectSearch(error)

    await expect(result).rejects.toBe(error)
    expect(handleUnexpectedError).toHaveBeenCalledOnce()
  })
})
