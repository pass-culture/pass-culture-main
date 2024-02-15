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
          end: '2024-01-29T23:00:28.040559Z',
          start: '2024-01-23T23:00:28.040547Z',
        },
      })

      expect(datesText).toEqual('Du 23 janvier au 29 janvier 2024 à 23h')
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
          beginningDatetime: '2024-01-29T23:00:28.040559Z',
        },
      })

      expect(dateText).toEqual('Le 29 janvier 2024 à 23:00')
    })

    it('should not return a date if the beginning of the offer does not exist', () => {
      const dateText = getFormattedDatesForBookableOffer({
        ...defaultCollectiveOffer,
        stock: {
          ...defaultCollectiveOffer.stock,
          beginningDatetime: undefined,
        },
      })

      expect(dateText).toEqual(null)
    })
  })
})
