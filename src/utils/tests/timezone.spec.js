import timezone from '../timezone'

describe('src | utils | strings | timezone', () => {
  it('should return America/Cayenne when departementCode is 97', () => {
    expect(timezone('97')).toEqual('America/Cayenne')
  })
  it('should return America/Cayenne when departementCode is 973', () => {
    expect(timezone('973')).toEqual('America/Cayenne')
  })
  it('should return Europe/Paris by default', () => {
    expect(timezone('')).toEqual('Europe/Paris')
  })
})
