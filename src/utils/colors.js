import { rgb_to_hsv as rgbToHsv } from 'colorsys'

export function getHeaderColor(firstThumbDominantColor) {
  if (!firstThumbDominantColor) {
    return 'black'
  }
  const [red, green, blue] = firstThumbDominantColor
  const { h } = rgbToHsv(red, green, blue)
  if (h) {
    return `hsl(${h}, 100%, 7.5%)`
  }
  return 'black'
}

export default getHeaderColor
