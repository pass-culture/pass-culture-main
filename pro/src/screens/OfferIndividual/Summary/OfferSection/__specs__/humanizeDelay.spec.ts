import humanizeDelay from '../utils'

describe('humanizeDelay', () => {
  it('should render the correct delay', () => {
    expect(humanizeDelay(900)).toStrictEqual('15 minutes')
    expect(humanizeDelay(3600)).toStrictEqual('1 heure')
    expect(humanizeDelay(7200)).toStrictEqual('2 heures')
    expect(humanizeDelay(259200)).toStrictEqual('3 jours')
  })
})
