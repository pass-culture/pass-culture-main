import { rgb_to_hsv } from 'colorsys'

export function getHeaderColor(firstThumbDominantColor = []) {

  console.log('firstThumbDominantColor', firstThumbDominantColor)

  const [red, green, blue] = firstThumbDominantColor
  const { h } = rgb_to_hsv(red, green, blue)
  if (h) {
    return `hsl(${h}, 100%, 7.5%)`
  }
  return 'black'
}
