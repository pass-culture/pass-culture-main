const sanitizeCoordinates = input => {
  const stringNumberWithoutComa = String(input).replace(',', '.')
  const isNegativeNumber = parseFloat(stringNumberWithoutComa) < 0
  const stringNumberWithoutTrailingNumbers = stringNumberWithoutComa.replace(
    /[^0-9.]/g,
    ''
  )

  let result = parseFloat(stringNumberWithoutTrailingNumbers)

  if (isNaN(result)) {
    return 0.0
  }

  if (isNegativeNumber) {
    result = -result
  }

  return result
}

export default sanitizeCoordinates
