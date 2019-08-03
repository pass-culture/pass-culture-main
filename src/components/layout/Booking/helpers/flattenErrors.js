const flattenErrors = (acc, err) => {
  let value = err
  if (Array.isArray(err)) value = Array.prototype.concat.apply([], err)
  return acc.concat(value)
}

export default flattenErrors
