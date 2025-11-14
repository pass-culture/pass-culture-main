import { getCollectiveOfferColumns } from './CollectiveOfferColumns'

describe('getCollectiveOfferColumns', () => {
  it('should contain 5 columns when isBookableTable is false', () => {
    const columns = getCollectiveOfferColumns({}, false)
    expect(columns).toHaveLength(5)
    expect(columns.map((col) => col.id)).toEqual([
      'name',
      'dates',
      'location',
      'status',
      'actions',
    ])
  })
  it('should contain 7 columns when isBookableTable is true', () => {
    const columns = getCollectiveOfferColumns({}, true)
    expect(columns).toHaveLength(7)
    expect(columns.map((col) => col.id)).toEqual([
      'name',
      'dates',
      'priceAndParticipants',
      'institution',
      'location',
      'status',
      'actions',
    ])
  })
})
