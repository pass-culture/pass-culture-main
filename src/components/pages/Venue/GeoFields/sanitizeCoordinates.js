function sanitizeCoordinates(input) {
  let result = parseFloat(
    String(input)
      .replace(',', '.')
      .replace(/[^0-9.]/g, '')
  )
  if (isNaN(result)) {
    return 0.0
  }

  if (input < 0) {
    result = -result
  }

  return result
}

export default sanitizeCoordinates
