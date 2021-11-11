export const getOffset = () => {
  const offsetInMinutes = new Date().getTimezoneOffset()
  const offSetSign = Math.sign(offsetInMinutes)
  const absoluteOffsetInHours = Math.abs(offsetInMinutes) / 60

  const signValue = offSetSign === 1 ? '-' : '+'
  const offsetValue =
    absoluteOffsetInHours <= 9 ? `0${absoluteOffsetInHours}` : `${absoluteOffsetInHours}`

  return `${signValue}${offsetValue}:00`
}
