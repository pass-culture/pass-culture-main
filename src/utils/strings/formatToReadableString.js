export const formatToReadableString = input => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}
