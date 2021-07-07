import { RESULT_FIELDS } from './constants'

// eslint-disable-next-line no-unused-vars
export const buildQueryOptions = params => {
  // TODO(antoinewg) use params to build the search options
  return {
    result_fields: RESULT_FIELDS,
    filters: {},
    page: {
      current: 1,
      size: params.hitsPerPage || 20,
    },
  }
}
