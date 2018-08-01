export default text => {
  const isstring = text && typeof text === 'string'
  if (!isstring) return ''
  const str = text.trim()
  return str.charAt(0).toUpperCase() + str.slice(1)
}
