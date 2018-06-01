export function getResolvedData(previousData, nextData, config = {}) {

  // unpack the config
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

  // no need to go further if no previous data
  if (!previousData) {
    return nextData
  }

  // add
  if (add === 'append') {
    if (isMutatingArray) {
      return previousData.concat(nextData)
    } else {
      nextData.forEach(nextDatum => previousData.push(nextDatum))
    }
  } else if (add === 'prepend') {
    if (isMutatingArray) {
      return nextData.concat(previousData)
    } else {
      return nextData.forEach(nextDatum => previousData.unshift(nextDatum))
    }
  }

  // no need to go further when we want just to trigger
  // a new fresh assign with nextData
  if (!isMergingArray) {
    return nextData
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

  // return
  return resolvedData
}
