function sanitizeCoordinates(input) {
  const result = parseFloat(
    String(input)
      .replace(',', '.')
      .replace(/[^0-9.]/g, '')
  )
  if (isNaN(result)) {
    return 0.0
  }

  return result
}

export default sanitizeCoordinates
