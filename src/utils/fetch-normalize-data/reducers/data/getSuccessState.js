import getStateKeyFromConfig from '../../fetch/stateKey/getStateKeyFromConfig'
import { successStatusCodesWithDataOrDatum } from '../../fetch/status'
import getNormalizedDeletedState from '../../normalize/getNormalizedDeletedState'
import getNormalizedMergedState from '../../normalize/getNormalizedMergedState'

export function getPatchFromStateKeyAndPayload(stateKey, payload) {
  const { datum } = payload
  let { data } = payload
  if (!data) {
    if (datum) {
      data = [datum]
    } else {
      data = []
    }
  }
  const patch = { [stateKey]: data }

  return patch
}

export const getSuccessState = (state, action) => {
  const { config, payload } = action
  const { status } = payload
  const { method, normalizer } = config

  const stateKey = getStateKeyFromConfig(config)

  if (!successStatusCodesWithDataOrDatum.includes(status)) {
    return Object.assign({}, state)
  }

  if (!stateKey) return state

  const patch = getPatchFromStateKeyAndPayload(stateKey, payload)

  const normalizerConfig = Object.assign({ normalizer }, config)
  if (normalizer) {
    normalizerConfig.normalizer = {
      [stateKey]: {
        normalizer,
        stateKey,
      },
    }
  }

  return method === 'DELETE'
    ? getNormalizedDeletedState(state, patch, normalizerConfig)
    : getNormalizedMergedState(state, patch, normalizerConfig)
}

export default getSuccessState
