import { computeURLCollectiveOfferId } from '../computeURLCollectiveOfferId'

describe('computeURLCollectiveOfferId', () => {
  it('when offer is template', () => {
    expect(computeURLCollectiveOfferId(1, true)).toStrictEqual('T-1')
  })

  it('when offer is not template', () => {
    expect(computeURLCollectiveOfferId(1, false)).toStrictEqual('1')
  })
})
