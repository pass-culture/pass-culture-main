import { valueToPrice } from '../getDisplayPrice'

const formatDecimals = number => {
  const numberWithTwoDecimals = number ? number.toFixed(2) : 0
  const numberWithCommaNotDot = valueToPrice(numberWithTwoDecimals)
  return numberWithCommaNotDot.replace(',00', '')
}

export default formatDecimals
