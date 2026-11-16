import type { liteClient } from 'algoliasearch/lite'

import { markAlgoliaSearchErrorReported } from '@/commons/errors/algoliaSearchErrors'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'

export function monitorAlgoliaSearch(client: ReturnType<typeof liteClient>) {
  const search = client.search.bind(client)

  client.search = <T>(...args: Parameters<typeof client.search>) =>
    search<T>(...args).catch((error: unknown) => {
      const status =
        typeof error === 'object' &&
        error !== null &&
        'status' in error &&
        typeof error.status === 'number'
          ? error.status
          : undefined

      handleUnexpectedError(error, {
        isSilent: true,
        context: { operation: 'adage-offers-search', status },
      })
      markAlgoliaSearchErrorReported(error)
      throw error
    })

  return client
}
