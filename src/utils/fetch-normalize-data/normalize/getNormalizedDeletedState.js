import { getProcessedData } from './getProcessedData'
import { getDefaultDatumIdValue } from './utils'

export function getNormalizedDeletedState(state, patch, config) {
  const getDatumIdValue = config.getDatumIdValue || getDefaultDatumIdValue
  const nextState = config.nextState || {}

  Object.keys(patch).forEach(patchKey => {
    const data = patch[patchKey]
    if (!data) {
      return
    }

    const nextData = getProcessedData(data, config)

    const previousData = state[patchKey]
    if (!previousData) {
      nextState[patchKey] = nextData
      return
    }

    const nextDataIds = nextData.map(getDatumIdValue)
    const resolvedData = previousData.filter(
      previousDatum => !nextDataIds.includes(getDatumIdValue(previousDatum))
    )
    nextState[patchKey] = resolvedData
  })

  return nextState
}
