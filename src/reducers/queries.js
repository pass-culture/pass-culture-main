import get from 'lodash.get'

const PENDING = 'PENDING'
const SUCCESS = 'SUCCESS'
const FAIL = 'FAIL'

export default (state = [], action) => {
  const id = get(action, 'config.requestId')
  if (/REQUEST_DATA_(POST|PUT|DELETE|PATCH)_(.*)/.test(action.type)) {
    return state.concat({
      id,
      status: PENDING,
    })
  } else if (
    /(SUCCESS|FAIL)_DATA_(GET|POST|PUT|PATCH)_(.*)/.test(action.type)
  ) {
    return state
      .filter(s => s.status !== PENDING) // Delete the finished ones (SUCCESS/FAIL) in the next cycle
      .map(
        s =>
          s.id === id
            ? {
                id,
                status: action.type.indexOf(SUCCESS) === 0 ? SUCCESS : FAIL,
              }
            : s
      )
  }
  return state
}
