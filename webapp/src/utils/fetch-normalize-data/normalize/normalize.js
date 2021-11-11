import { getReshapedNormalizer } from './getReshapedNormalizer'

export function normalizeDataAtItem(data, datumKey, stateKey, config) {
  const { doWithNormalizedPatch } = config

  let normalizedData = []

  data.forEach(datum => {
    const normalizedValue = datum[datumKey]

    if (Array.isArray(normalizedValue)) {
      normalizedData = normalizedData.concat(normalizedValue)
      delete datum[datumKey]
    } else if (normalizedValue) {
      normalizedData.push(datum[datumKey])
      delete datum[datumKey]
    }
  })

  if (normalizedData.length) {
    if (doWithNormalizedPatch) {
      const singletonPatch = { [stateKey]: normalizedData }
      doWithNormalizedPatch(singletonPatch, config)
    }
  }
}

export function normalizeData(data, config) {
  const {
    isMergingDatum: globalIsMergingDatum,
    isMutatingDatum: globalIsMutatingDatum,
    normalizer,
  } = config

  const reshapedNormalizer = getReshapedNormalizer(normalizer)

  Object.keys(normalizer).forEach(datumKey => {
    const { isMergingDatum, isMutatingDatum, process, resolve, stateKey } = reshapedNormalizer[
      datumKey
    ]
    const subNormalizer = reshapedNormalizer[datumKey].normalizer || {}

    const subConfig = Object.assign({}, config, {
      isMergingDatum: typeof isMergingDatum !== 'undefined' ? isMergingDatum : globalIsMergingDatum,
      isMutatingDatum:
        typeof isMutatingDatum !== 'undefined' ? isMutatingDatum : globalIsMutatingDatum,
      normalizer: { [stateKey]: { normalizer: subNormalizer, stateKey } },
      process,
      resolve,
    })

    normalizeDataAtItem(data, datumKey, stateKey, subConfig)
  })
}

export function normalize(obj, config) {
  const { normalizer } = config
  if (normalizer) {
    const reshapedNormalizer = getReshapedNormalizer(normalizer)

    Object.keys(reshapedNormalizer).forEach(datumKey => {
      const data = obj[datumKey]

      const subNormalizer = reshapedNormalizer[datumKey].normalizer
      if (!subNormalizer) {
        return
      }

      const subConfig = Object.assign({}, config, { normalizer: subNormalizer })

      normalizeData(data, subConfig)
    })
  }
}
