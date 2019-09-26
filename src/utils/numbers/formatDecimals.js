const formatDecimals = number => {
  const numberWithTwoDecimals = number.toFixed(2)
  return numberWithTwoDecimals.replace('.00', '')
}

export default formatDecimals
