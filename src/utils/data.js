export function getNextState(state, method, key, nextData, config = {}) {

  // UNPACK
  const {
    add,
    isMergingDatum,
    isMutatingDatum
  } = config
  const isMergingArray = typeof config.isMergingArray === 'undefined'
    ? true
    : config.isMergingArray
  const isMutatingArray = typeof config.isMutatingArray === 'undefined'
    ? true
    : config.isMutatingArray
  const nextState = config.nextState || {}
  const previousData = state[key]

  // NORMALIZER
  if (config.normalizer) {
    Object.keys(config.normalizer)
          .forEach(key => {

            let nextNormalizedData = []
            nextData.forEach(nextDatum => {
              if (Array.isArray(nextDatum[key])) {
                nextNormalizedData = nextNormalizedData.concat(nextDatum[key])
                delete nextDatum[key]
              } else if (nextDatum[key]) {
                nextNormalizedData.push(nextDatum[key])
                delete nextDatum[key]
              }
            })

            if (nextNormalizedData.length) {
              const nextNormalizedState = getNextState(
                state,
                null,
                config.normalizer[key],
                nextNormalizedData,
                Object.assign({ nextState })
              )
              Object.assign(nextState, nextNormalizedState)
            }

          })
  }

  // no need to go further if no previous data
  if (!previousData) {
    nextState[key] = nextData
    return nextState
  }

  // DELETE CASE
  if (method === 'DELETE') {
    const resolvedData = [...previousData]
    nextData.forEach(nextDatum => {
      const resolvedIndex = resolvedData.findIndex(resolvedDatum =>
          resolvedDatum.id === nextDatum.id)
      if (typeof resolvedIndex !== 'undefined') {
        delete resolvedData[resolvedIndex]
      }
    })
    nextState[key] = nextData
    return nextState
  }

  // GET POST PATCH

  // add
  if (add === 'append') {
    if (isMutatingArray) {
      nextState[key] = previousData.concat(nextData)
      return nextState
    }
    nextData.forEach(nextDatum => previousData.push(nextDatum))
  } else if (add === 'prepend') {
    if (isMutatingArray) {
      nextState[key] = nextData.concat(previousData)
      return nextState
    }
    nextState[key] = nextData.forEach(nextDatum =>
      previousData.unshift(nextDatum))
    return nextState
  }

  // no need to go further when we want just to trigger
  // a new fresh assign with nextData
  if (!isMergingArray) {
    nextState[key] = nextData
    return nextState
  }

  // Determine first if we are going to trigger a mutation of the array
  const resolvedData = isMutatingArray
    ? [...previousData]
    : previousData

  // for each datum we are going to assign (by merging or not) them into
  // their right place in the resolved array
  nextData.forEach(nextDatum => {
    const previousIndex = previousData.findIndex(previousDatum =>
      previousDatum.id === nextDatum.id)
    const resolvedIndex = previousIndex === -1
      ? resolvedData.length
      : previousIndex
    const datum = isMutatingDatum
      ? Object.assign({}, isMergingDatum && previousData[previousIndex], nextDatum)
      : isMergingDatum
        ? previousIndex !== -1
          ? Object.assign(previousData[previousIndex], nextDatum)
          : nextDatum
        : nextDatum
    resolvedData[resolvedIndex] = datum
  })

  // set
  nextState[key] = nextData

  // return
  return nextState
}
