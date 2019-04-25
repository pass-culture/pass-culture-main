import get from 'lodash.get'

const isValidObject = obj => typeof obj === 'object' && !Array.isArray(obj)

const shouldShowVerso = match => {
  if (!match || !isValidObject(match)) return false

  const params = get(match, 'params', false)
  if (!params || !isValidObject(params)) return false

  const view = get(match, 'params.view', false)
  const mediationId = get(match, 'params.mediationId', false)
  if (!mediationId && !view) return false

  const mediationIdUseVerso = mediationId === 'verso' && view !== 'verso'
  const viewUseVerso = view === 'verso'
  return mediationIdUseVerso || viewUseVerso
}

export default shouldShowVerso
