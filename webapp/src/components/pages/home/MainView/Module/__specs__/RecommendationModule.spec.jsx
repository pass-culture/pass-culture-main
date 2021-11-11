import { PANE_LAYOUT } from '../../domain/layout'
import { mount } from 'enzyme'
import RecommendationModule from '../RecommendationModule'
import React from 'react'
import { MemoryRouter } from 'react-router'
import OfferTile from '../OfferTile/OfferTile'
import { getStubStore } from '../../../../../../utils/stubStore'
import { Provider } from 'react-redux'
import RecommendationPane from '../../domain/ValueObjects/RecommendationPane'

let mockInView = jest.fn()
jest.mock('react-intersection-observer', () => ({
  useInView: () => ({
    ref: jest.fn(),
    inView: mockInView,
  }),
}))

describe('src | components | RecommendationModule', () => {
  let display
  let offerOne
  let offerTwo
  let props
  let mockStore

  beforeEach(() => {
    display = {
      activeOn: '2020-07-01T00:00+02:00',
      activeUntil: '2020-07-30T00:00+02:00',
      layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
      minOffers: 1,
      title: 'Tes offres recommmandées!',
    }
    offerOne = {
      objectID: '105',
      offer: {
        dates: [],
        id: 'NE',
        label: 'Cinéma',
        name: "Dansons jusqu'en 2030",
        prices: [33],
        thumbUrl: 'http://localhost/storage/thumbs/mediations/KQ',
      },
      venue: {
        name: 'Le Sous-sol',
      },
    }
    offerTwo = {
      objectID: '1',
      offer: {
        dates: [],
        id: 'AE',
        label: 'Presse',
        name: 'Naruto',
        prices: [1, 12],
        thumbUrl: 'http://localhost/storage/thumbs/mediations/PP',
      },
      venue: {
        name: 'Librairie Kléber',
      },
    }
    props = {
      historyPush: jest.fn(),
      hits: [],
      module: null,
      row: 1,
      trackAllTilesSeen: jest.fn(),
      trackConsultOffer: jest.fn(),
      trackRecommendationModuleSeen: jest.fn(),
    }
    mockStore = getStubStore({
      data: (state = {}) => state,
    })
  })

  it('should render two OfferTile when two offers', async () => {
    // given
    props.hits = [offerOne, offerTwo]
    props.module = new RecommendationPane({ display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <RecommendationModule {...props} />
      </MemoryRouter>
    )

    await wrapper.update()

    // then
    const offers = wrapper.find(RecommendationModule).find(OfferTile)
    expect(offers).toHaveLength(2)
    const firstOffer = offers.at(0)
    expect(firstOffer.prop('hit')).toStrictEqual(offerOne)
    const secondOffer = offers.at(1)
    expect(secondOffer.prop('hit')).toStrictEqual(offerTwo)
  })

  it('should render a pane with a title', async () => {
    // given
    props.hits = [offerOne]
    props.module = new RecommendationPane({ display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <RecommendationModule {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const title = wrapper.find(RecommendationModule).find({ children: 'Tes offres recommmandées!' })
    expect(title).toHaveLength(1)
  })

  describe('when layout is two tiles', () => {
    it('should render two offer tiles', async () => {
      // given
      props.hits = [offerOne, offerTwo]
      display.layout = PANE_LAYOUT['TWO-ITEMS']
      props.module = new RecommendationPane({ display })

      // when
      const wrapper = await mount(
        <Provider store={mockStore}>
          <MemoryRouter>
            <RecommendationModule {...props} />
          </MemoryRouter>
        </Provider>
      )
      await wrapper.update()

      // then
      const offerTiles = wrapper.find(OfferTile)
      expect(offerTiles).toHaveLength(2)
    })
  })

  describe('tiles tracking', () => {
    describe('only one tile', () => {
      it('should not track user on render for last tile seen if there is only one tile', async () => {
        // Given
        props.hits = [offerOne]
        props.module = new RecommendationPane({ display })

        // When
        await mount(
          <MemoryRouter>
            <RecommendationModule {...props} />
          </MemoryRouter>
        )

        // Then
        expect(props.trackAllTilesSeen).not.toHaveBeenCalled()
      })
    })

    describe('multiple tiles', () => {
      let tilesWrapper
      let offerThree

      beforeEach(async () => {
        offerThree = {
          objectID: '9',
          offer: {
            dates: [],
            id: 'BF',
            label: 'Presse',
            name: 'Naruto',
            prices: [1, 12],
            thumbUrl: 'http://localhost/storage/thumbs/mediations/PP',
          },
          venue: {
            name: 'Librairie Kléber',
          },
        }
        props.hits = [offerOne, offerTwo, offerThree]
        props = {
          ...props,
          module: new RecommendationPane({ display }),
        }

        const wrapper = await mount(
          <MemoryRouter>
            <RecommendationModule {...props} />
          </MemoryRouter>
        )
        wrapper.update()
        tilesWrapper = wrapper.find('ul').children()
      })

      it('should not track user if tile seen is not the last', () => {
        // When
        tilesWrapper.invoke('onChangeIndex')(1)

        // Then
        expect(props.trackAllTilesSeen).not.toHaveBeenCalled()
      })

      it('should track user if tile seen is the last one', () => {
        // When
        tilesWrapper.invoke('onChangeIndex')(1)
        tilesWrapper.invoke('onChangeIndex')(2)

        // Then
        expect(props.trackAllTilesSeen).toHaveBeenCalledTimes(1)
        expect(props.trackAllTilesSeen).toHaveBeenCalledWith(display.title, 3)
      })

      it('should track user only once if last tile is seen multiple times', () => {
        // When
        tilesWrapper.invoke('onChangeIndex')(1)
        tilesWrapper.invoke('onChangeIndex')(2)
        tilesWrapper.invoke('onChangeIndex')(1)
        tilesWrapper.invoke('onChangeIndex')(2)

        // Then
        expect(props.trackAllTilesSeen).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('recommendation module tracking', () => {
    it('should not log RecommendationModuleSeen if it does not appear in the viewport', async () => {
      // Given
      mockInView = false
      props.hits = [offerOne]
      props.module = new RecommendationPane({ display })

      // When
      await mount(
        <MemoryRouter>
          <RecommendationModule {...props} />
        </MemoryRouter>
      )

      // Then
      expect(props.trackRecommendationModuleSeen).not.toHaveBeenCalled()
    })

    it('should log RecommendationModuleSeen if it does appear in the viewport', async () => {
      // Given
      mockInView = true
      props.hits = [offerOne]
      props.module = new RecommendationPane({ display })

      // When
      await mount(
        <MemoryRouter>
          <RecommendationModule {...props} />
        </MemoryRouter>
      )

      // Then
      expect(props.trackRecommendationModuleSeen).toHaveBeenCalledTimes(1)
      expect(props.trackRecommendationModuleSeen).toHaveBeenCalledWith(
        'Tes offres recommmandées!',
        1
      )
    })
  })
})
