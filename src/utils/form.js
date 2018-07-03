import get from 'lodash.get'

export function getIsDisabled (form, keys, isNew) {
  return !form ||
    isNew
      ? keys.filter(f => typeof get(form, f) === 'undefined').length
      : keys.every(f => typeof get(form, f) === 'undefined')
}

export function optionify(
  collection,
  placeholder,
  mapFn=(el => ({label: el.name, value: el.id}))
) {
  const collectionWithPlaceholder = collection.length > 1
    ? [{label: placeholder}].concat(collection)
    : collection
  return collectionWithPlaceholder.map(mapFn)
}
