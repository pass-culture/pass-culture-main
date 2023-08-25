import { getDistance } from 'utils/getDistance'

describe('getDistance', () => {
  it('should return the distance between two points', () => {
    const ParisCoordinates = {
      latitude: 48.85661,
      longitude: 2.351499,
    }
    const LyonCoordinates = {
      latitude: 45.757814,
      longitude: 4.832011,
    }

    const distance = getDistance(ParisCoordinates, LyonCoordinates)
    // The distance between Paris and Lyon is 392km using this website:
    // https://www.distance.to/Paris,%C3%8Ele-de-France,FRA/Lyon,Rh%C3%B4ne,Auvergne-Rh%C3%B4ne-Alpes,FRA
    expect(distance).toBe(392)
  })
})
