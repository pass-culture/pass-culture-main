import { buildPlaceLabel } from '../buildPlaceLabel'

describe('src | utils | buildPlaceLabel', () => {
  it('should return the default label when place is null', () => {
    // given
    const place = null

    // when
    const placeLabel = buildPlaceLabel(place)

    // then
    expect(placeLabel).toStrictEqual('Choisir un lieu')
  })

  it('should return the city name when the place is a city', () => {
    // given
    const place = {
      name: {
        long: 'Paris',
        short: 'Paris',
      }
    }

    // when
    const placeLabel = buildPlaceLabel(place)

    // then
    expect(placeLabel).toStrictEqual('Paris')
  })

  it('should return the address and the city name when the place is an adresse', () => {
    // given
    const place = {
      name: {
        long: '34 avenue de l\'opéra, Paris',
        short: '34 avenue de l\'opéra',
      }
    }

    // when
    const placeLabel = buildPlaceLabel(place)

    // then
    expect(placeLabel).toStrictEqual('34 avenue de l\'opéra, Paris')
  })
})
