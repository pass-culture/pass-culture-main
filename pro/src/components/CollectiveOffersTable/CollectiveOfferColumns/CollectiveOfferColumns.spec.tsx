import { getCollectiveOfferColumns } from './CollectiveOfferColumns'

describe('getCollectiveOfferColumns', () => {
  it('should contain 5 columns when isBookableTable is false', () => {
    const columns = getCollectiveOfferColumns({
      isBookableTable: false,
      isReadOnly: false,
    })
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
    const columns = getCollectiveOfferColumns({
      isBookableTable: true,
      isReadOnly: false,
    })
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
  it('should omit the actions column when isReadOnly is true', () => {
    const columns = getCollectiveOfferColumns({
      isBookableTable: true,
      isReadOnly: true,
    })
    expect(columns).toHaveLength(6)
    expect(columns.map((col) => col.id)).not.toContain('actions')
  })
})
