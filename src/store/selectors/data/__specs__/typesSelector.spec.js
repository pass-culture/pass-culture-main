import { selectTypesByIsVenueVirtual, selectTypeValueByOffer } from '../typesSelectors'

describe('src | selectors | data | typesSelectors', () => {
  describe('selectTypesByIsVenueVirtual', () => {
    let state

    beforeEach(() => {
      state = {
        data: {
          types: [
            {
              proLabel: 'Online',
              offlineOnly: false,
              onlineOnly: true,
            },
            {
              proLabel: 'Offline',
              offlineOnly: true,
              onlineOnly: false,
            },
          ],
        },
      }
    })

    it('should return all types when venue is undefined', () => {
      // given
      const isVenueVirtual = undefined

      // when
      const result = selectTypesByIsVenueVirtual(state, isVenueVirtual)

      // then
      expect(result).toStrictEqual([
        {
          proLabel: 'Offline',
          offlineOnly: true,
          onlineOnly: false,
        },
        {
          proLabel: 'Online',
          offlineOnly: false,
          onlineOnly: true,
        },
      ])
    })

    it('should return online type only when venue is virtual', () => {
      // given
      const isVenueVirtual = true

      // when
      const result = selectTypesByIsVenueVirtual(state, isVenueVirtual)

      // then
      expect(result).toStrictEqual([
        {
          proLabel: 'Online',
          offlineOnly: false,
          onlineOnly: true,
        },
      ])
    })

    it('should return offline type only when venue is not virtual', () => {
      // given
      const isVenueVirtual = false

      // when
      const result = selectTypesByIsVenueVirtual(state, isVenueVirtual)

      // then
      expect(result).toStrictEqual([
        {
          proLabel: 'Offline',
          offlineOnly: true,
          onlineOnly: false,
        },
      ])
    })

    it('sort result by proLabel', () => {
      // given
      state.data.types = [
        {
          proLabel: 'C',
          offlineOnly: false,
          onlineOnly: true,
        },
        {
          proLabel: 'A',
          offlineOnly: false,
          onlineOnly: true,
        },
        {
          proLabel: 'B',
          offlineOnly: false,
          onlineOnly: true,
        },
      ]
      const isVenueVirtual = true

      // when
      const result = selectTypesByIsVenueVirtual(state, isVenueVirtual)

      // then
      expect(result).toStrictEqual([
        {
          proLabel: 'A',
          offlineOnly: false,
          onlineOnly: true,
        },
        {
          proLabel: 'B',
          offlineOnly: false,
          onlineOnly: true,
        },
        {
          proLabel: 'C',
          offlineOnly: false,
          onlineOnly: true,
        },
      ])
    })
  })

  describe('selectTypeValueByOffer', () => {
    it('should return pro label for offer type', () => {
      // given
      const offer = {
        id: 'ABCD',
        type: 'ThingType.Lapin',
      }
      const state = {
        data: {
          types: [
            {
              value: 'théâtre',
              proLabel: 'Théâtre',
            },
            {
              value: 'ThingType.Lapin',
              proLabel: 'Jeannot Lapin',
            },
          ],
        },
      }
      // when
      const result = selectTypeValueByOffer(state, offer)

      // then
      expect(result).toStrictEqual('Jeannot Lapin')
    })

    it('should return activation label for activation offer', () => {
      // given
      const offer = {
        id: 'ABCD',
        type: 'ThingType.ACTIVATION',
      }
      const state = {
        data: {
          types: [
            {
              value: 'théâtre',
              proLabel: 'Théâtre',
            },
            {
              value: 'ThingType.Lapin',
              proLabel: 'Jeannot Lapin',
            },
          ],
        },
      }
      // when
      const result = selectTypeValueByOffer(state, offer)

      // then
      expect(result).toStrictEqual('Pass Culture : activation')
    })
  })
})
