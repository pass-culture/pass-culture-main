export const parseAPIErrors = errors => {
  if (!errors) return []
  let errs = errors
  if (errors && typeof errors === 'string') errs = { 0: errors }
  // si c'est un array on transforme en object, sinon reste un objet
  errs = errs && Array.isArray(errs) ? Object.assign({}, errs) : errs || {}
  // flatten object to array
  // errs = Object.keys(errs).reduce(acc, key => acc, [])
  return errs
  // if (!errors) return []
  // if (errors && Array.isArray(errors)) entries = Object.assign({}, errors)
  // if (errors && !Array.isArray(errors)) entries = Object.values(errors)
  // return entries
}

export default parseAPIErrors
