import uniqBy from 'lodash.uniqby'
import { getDefaultDatumIdKey, getDefaultDatumIdValue } from './utils'

export function getProcessedDatum(datum, index, config) {
  const { apiPath, data, process } = config
  const activityTag = config.activityTag || apiPath
  const getDatumIdKey = config.getDatumIdKey || getDefaultDatumIdKey
  const getDatumIdValue = config.getDatumIdValue || getDefaultDatumIdValue

  let processedDatum = Object.assign(
    { [getDatumIdKey(datum)]: getDatumIdValue(datum, index) },
    datum
  )

  if (activityTag) {
    if (!processedDatum.__ACTIVITIES__) {
      processedDatum.__ACTIVITIES__ = [activityTag]
    } else {
      processedDatum.__ACTIVITIES__.push(activityTag)
    }
  }

  if (process) {
    processedDatum = config.process(processedDatum, data, config)
  }

  return processedDatum
}

export function getProcessedData(data, config) {
  const getDatumIdValue = config.getDatumIdValue || getDefaultDatumIdValue
  const unifyConfig = Object.assign({ data }, config)

  const processedData = data.map((datum, index) => getProcessedDatum(datum, index, unifyConfig))

  return uniqBy(processedData, getDatumIdValue)
}
