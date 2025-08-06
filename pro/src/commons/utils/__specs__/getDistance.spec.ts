// Distance using https://www.sunearthtools.com/fr/tools/distance.php
// Center (EiffelTourCoordinates): {latitude: 48.85, longitude: 2.29 }

import { getHumanizeRelativeDistance } from '@/commons/utils/getDistance'

describe('getDistance', () => {
  it.each`
    lat      | lng       | actualDistance (m) | expected
    ${48.85} | ${2.2901} | ${7.3}             | ${'7 m'}
    ${48.85} | ${2.2902} | ${14.6}            | ${'15 m'}
    ${48.85} | ${2.291}  | ${73.2}            | ${'75 m'}
    ${48.85} | ${2.292}  | ${146.4}           | ${'150 m'}
    ${48.85} | ${2.33}   | ${2927.6}          | ${'2,9 km'}
    ${48.85} | ${2.39}   | ${7319.1}          | ${'7 km'}
    ${48.85} | ${102.39} | ${6739182.6}       | ${'900+ km'}
  `(
    'getHumanizeRelativeDistance($actualDistance) \t= $expected',
    ({ lat, lng, expected }) => {
      expect(
        getHumanizeRelativeDistance(
          {
            latitude: lat,
            longitude: lng,
          },
          { latitude: 48.85, longitude: 2.29 }
        )
      ).toBe(expected)
    }
  )
})
