import { computeURLCollectiveOfferId } from '../computeURLCollectiveOfferId'

describe('computeURLCollectiveOfferId', () => {
  it('when offer is template', () => {
    expect(computeURLCollectiveOfferId('A1', true)).toStrictEqual('T-A1')
  })

  it('when offer is not template', () => {
    expect(computeURLCollectiveOfferId('A1', false)).toStrictEqual('A1')
  })
})
