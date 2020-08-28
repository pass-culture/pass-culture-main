import { getDefaultDatumIdValue, merge } from './utils'

export function getMergedData(nextData, previousData, config) {
  if (!previousData) {
    return nextData
  }

  const { isMergingDatum, isMutatingDatum, resolve } = config
  const getDatumIdValue = config.getDatumIdValue || getDefaultDatumIdValue
  const isMutatingArray =
    typeof config.isMutatingArray === 'undefined' ? true : config.isMutatingArray

  const mergedData = isMutatingArray ? [...previousData] : previousData

  // for each datum we are going to assign (by merging or not) them into
  // their right place in the resolved array
  nextData.forEach(nextDatum => {
    const previousIndex = previousData.findIndex(
      previousDatum => getDatumIdValue(previousDatum) === getDatumIdValue(nextDatum)
    )
    const resolvedIndex = previousIndex === -1 ? mergedData.length : previousIndex

    let datum

    if (resolve) {
      datum = resolve(nextDatum, previousData[previousIndex], {
        previousData,
        nextData,
        config,
      })
    } else if (isMutatingDatum) {
      datum = Object.assign({}, isMergingDatum && previousData[previousIndex], nextDatum)
    } else if (isMergingDatum) {
      datum = previousIndex !== -1 ? merge(previousData[previousIndex], nextDatum) : nextDatum
    } else {
      datum = nextDatum
    }

    mergedData[resolvedIndex] = datum
  })

  return mergedData
}
