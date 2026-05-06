import { describe, expect, it, vi } from 'vitest'

import { apiNew } from '@/apiClient/api'
import * as serializeApiCollectiveFiltersModule from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import * as downloadFileModule from '@/commons/utils/downloadFile'

import { downloadBookableOffersFile } from '../downloadBookableOffersFile'

vi.mock('@/commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
}))

vi.mock('@/commons/core/Offers/utils/serializeApiCollectiveFilters', () => ({
  serializeApiCollectiveFilters: vi.fn(),
}))

const serializedFilters = {
  name: null,
  offererId: 1,
  venueId: null,
  status: null,
  periodBeginningDate: null,
  periodEndingDate: null,
  format: null,
  locationType: null,
  offererAddressId: null,
}

const baseFilters = {
  name: '',
  venueId: 'all' as const,
  status: [],
  periodBeginningDate: '',
  periodEndingDate: '',
  format: 'all' as const,
  offererId: '1',
}

describe('downloadBookableOffersFile', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-03-15'))
    vi.spyOn(
      serializeApiCollectiveFiltersModule,
      'serializeApiCollectiveFilters'
    ).mockReturnValue(serializedFilters)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('CSV', () => {
    it('should call getCollectiveOffersCsv and download the file with correct name', async () => {
      const csvContent = 'col1,col2\nval1,val2'
      vi.spyOn(apiNew, 'getCollectiveOffersCsv').mockResolvedValue(csvContent)

      await downloadBookableOffersFile(baseFilters, 'CSV')

      expect(apiNew.getCollectiveOffersCsv).toHaveBeenCalledWith({
        query: serializedFilters,
      })

      expect(downloadFileModule.downloadFile).toHaveBeenCalledWith(
        expect.any(Blob),
        'offres-reservables-20250315.csv'
      )
    })
  })

  describe('XLS', () => {
    it('should call getCollectiveOffersExcel and download the file with correct name', async () => {
      const excelBlob = new Blob(['excel content'], {
        type: 'application/vnd.ms-excel',
      })

      vi.spyOn(apiNew, 'getCollectiveOffersExcel').mockResolvedValue(excelBlob)

      await downloadBookableOffersFile(baseFilters, 'XLS')

      expect(apiNew.getCollectiveOffersExcel).toHaveBeenCalledWith({
        query: serializedFilters,
      })

      expect(downloadFileModule.downloadFile).toHaveBeenCalledWith(
        excelBlob,
        'offres-reservables-20250315.xls'
      )
    })
  })
})
