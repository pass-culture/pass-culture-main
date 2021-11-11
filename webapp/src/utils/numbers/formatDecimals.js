import { formatToFrenchDecimal } from '../getDisplayPrice'

const formatDecimals = number => {
  const numberWithTwoDecimals = number ? number.toFixed(2) : 0
  const numberWithCommaNotDot = formatToFrenchDecimal(numberWithTwoDecimals)
  const numberWithoutDoubleZero = numberWithCommaNotDot.replace(',00', '')
  return numberWithoutDoubleZero
}

export default formatDecimals
