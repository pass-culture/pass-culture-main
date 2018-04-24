import get from 'lodash.get'

const PENDING = 'PENDING'
const SUCCESS = 'SUCCESS'
const FAILED = 'FAILED'

export default (state=[], action) => {
  const id = get(action, 'config.requestId')
  if (/REQUEST_DATA_(POST|PUT|DELETE|PATCH)_(.*)/.test(action.type)) {
    return state.concat({
      id,
      status: PENDING,
    })
  } else if (/SUCCESS_DATA_(GET|POST|PUT|PATCH)_(.*)/.test(action.type)) {
    return state.map(s => s.id === id ? {id, status: SUCCESS} : s)
  } else if (/FAIL_DATA_(GET|POST|PUT|PATCH)_(.*)/.test(action.type)) {
    return state.map(s => s.id === id ? {id, status: FAILED} : s)
  }
  return state
}