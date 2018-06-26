import uniqBy from 'lodash.uniqby'

export function getNextState(state, method, patch, config = {}) {

  // UNPACK
  const {
    normalizer,
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

  if (!patch) {
    return state
  }


  // LOOP OVER ALL THE KEYS
  for (let key of Object.keys(patch)) {

    // PREVIOUS
    const previousData = state[key]

    // CLONE
    // FORCE TO GIVE AN ID
    // UNIFY BY ID
    // (BECAUSE DEEPEST NORMALIZED DATA CAN RETURN ARRAY OF SAME ELEMENTS)
    const data = patch[key]
    if (!data) {
      continue
    }
    const nextData = uniqBy(
      data.map((datum, index) =>
        Object.assign({ id: index }, datum)),
      datum => datum.id
    )


    // NORMALIZER
    if (normalizer) {
      Object.keys(normalizer)
            .forEach(key => {

              let nextNormalizedData = []
              nextData.forEach(nextDatum => {
                if (Array.isArray(nextDatum[key])) {
                  nextNormalizedData = nextNormalizedData.concat(nextDatum[key])
                  // replace by an array of ids
                  nextDatum[`${key}Ids`] = nextDatum[key].map(d => d.id)
                  // delete
                  delete nextDatum[key]
                } else if (nextDatum[key]) {
                  nextNormalizedData.push(nextDatum[key])
                  delete nextDatum[key]
                }
              })

              if (nextNormalizedData.length) {

                // ADAPT BECAUSE NORMALIZER VALUES
                // CAN BE DIRECTLY THE STORE KEYS IN THE STATE
                // OR AN OTHER CHILD NORMALIZER CONFIG
                // IN ORDER TO BE RECURSIVELY EXECUTED
                let nextNormalizer
                let storeKey
                if (typeof normalizer[key] === 'string') {
                  storeKey = normalizer[key]
                } else {
                  storeKey = normalizer[key].key
                  nextNormalizer = normalizer[key].normalizer
                }

                // RECURSIVE CALL TO MERGE THE DEEPER NORMALIZED VALUE
                const nextNormalizedState = getNextState(
                  state,
                  null,
                  { [storeKey]: nextNormalizedData },
                  { nextState, normalizer: nextNormalizer }
                )

                // MERGE THE CHILD NORMALIZED DATA INTO THE
                // CURRENT NEXT STATE
                Object.assign(nextState, nextNormalizedState)
              }

            })
    }

    // no need to go further if no previous data
    if (!previousData) {
      nextState[key] = nextData
      continue
    }

    // DELETE CASE
    if (method === 'DELETE') {
      const nextDataIds = nextData.map(nextDatum => nextDatum.id)
      const resolvedData = previousData.filter(previousDatum =>
        !nextDataIds.includes(previousDatum.id))
      nextState[key] = resolvedData
      continue
    }

    // GET POST PATCH

    // no need to go further when we want just to trigger
    // a new fresh assign with nextData
    if (!isMergingArray) {
      nextState[key] = nextData
      continue
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
    nextState[key] = resolvedData
  }

  // return
  return nextState
}
