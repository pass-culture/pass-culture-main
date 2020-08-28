export function getDefaultDatumIdKey() {
  return 'id'
}

export function getDefaultDatumIdValue(datum, index) {
  return datum.id || index
}

export function getDefaultCommitFrom() {
  return {}
}

export const merge = (target, source) => {
  for (const key of Object.keys(source)) {
    if (source[key] instanceof Object) Object.assign(
      source[key],
      merge(target[key],
        source[key]))
  }
  Object.assign(target || {}, source)
  return target
}
