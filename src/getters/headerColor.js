import { rgb_to_hsv } from 'colorsys'
import get from 'lodash.get';

export default function getHeaderColor (mediation, source) {
  const [red, green, blue] =
    get(mediation, 'firstThumbDominantColor') ||
    get(source, 'firstThumbDominantColor') || []
    const {h} = rgb_to_hsv(red, green, blue);
    if (h) {
      return `hsl(${h}, 100%, 7.5%)`;
    }
    return 'black';
}
