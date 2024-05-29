import {
  defaultCollectiveTemplateOffer,
  defaultCollectiveOffer,
} from 'utils/adageFactories'

import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '../adageOfferDates'

describe('adageOfferDates', () => {
  describe('getFormattedDatesForTemplateOffer', () => {
    it('should show the dates of a template offer that has specific dates', () => {
      const datesText = getFormattedDatesForTemplateOffer({
        ...defaultCollectiveTemplateOffer,
        dates: {
          end: '2024-01-30T00:00:28.040559Z',
          start: '2024-01-24T00:00:28.040547Z',
        },
      })

      expect(datesText).toEqual('Du 24 janvier au 30 janvier 2024')
    })

    it('should show that the offer is permanent if it has no dates', () => {
      const datesText = getFormattedDatesForTemplateOffer({
        ...defaultCollectiveTemplateOffer,
        dates: undefined,
      })

      expect(datesText).toEqual(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    })
  })

  describe('getFormattedDatesForBookableOffer', () => {
    it('should return the date of the beginning of the offer', () => {
      const dateText = getFormattedDatesForBookableOffer({
        ...defaultCollectiveOffer,
        stock: {
          ...defaultCollectiveOffer.stock,
          startDatetime: '2024-01-29T23:00:28.040559Z',
        },
      })

      expect(dateText).toEqual('Le 30 janvier 2024 à 00:00')
    })

    it('should not return a date if the beginning of the offer does not exist', () => {
      const dateText = getFormattedDatesForBookableOffer({
        ...defaultCollectiveOffer,
        stock: {
          ...defaultCollectiveOffer.stock,
          startDatetime: undefined,
        },
      })

      expect(dateText).toEqual(null)
    })
  })
})
