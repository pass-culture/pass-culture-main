import Offers from '../../domain/ValueObjects/Offers'
import { PANE_LAYOUT } from '../../domain/layout'
import { mount } from 'enzyme'
import Module from '../Module'
import React from 'react'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import { MemoryRouter } from 'react-router'
import OfferTile from '../OfferTile/OfferTile'
import OffersWithCover from '../../domain/ValueObjects/OffersWithCover'
import SeeMore from '../SeeMore/SeeMore'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('src | components | Module', () => {
  let algolia
  let display
  let offerOne
  let offerTwo
  let geolocation
  let props

  beforeEach(() => {
    algolia = {
      aroundRadius: null,
      beginningDatetime: null,
      categories: ['CINEMA', 'LECON', 'LIVRE'],
      endingDatetime: null,
      hitsPerPage: 3,
      isDigital: false,
      isDuo: true,
      isFree: false,
      isEvent: true,
      isGeolocated: false,
      isThing: true,
      newestOnly: true,
      priceMax: 10,
      priceMin: 1,
      title: 'Mes paramètres Algolia',
    }
    display = {
      activeOn: '2020-07-01T00:00+02:00',
      activeUntil: '2020-07-30T00:00+02:00',
      layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
      minOffers: 1,
      title: 'Les offres près de chez toi!',
    }
    geolocation = {
      latitude: 1,
      longitude: 2,
    }
    offerOne = {
      objectID: 'NE',
      offer: {
        dates: [],
        id: 'NE',
        label: 'Cinéma',
        name: "Dansons jusqu'en 2030",
        priceMax: 33,
        priceMin: 33,
        thumbUrl: 'http://localhost/storage/thumbs/mediations/KQ',
      },
      venue: {
        name: 'Le Sous-sol',
      },
    }
    offerTwo = {
      objectID: 'AE',
      offer: {
        dates: [],
        id: 'AE',
        label: 'Presse',
        name: 'Naruto',
        priceMax: 1,
        priceMin: 12,
        thumbUrl: 'http://localhost/storage/thumbs/mediations/PP',
      },
      venue: {
        name: 'Librairie Kléber',
      },
    }
    props = {
      geolocation,
      historyPush: jest.fn(),
      module: null,
      row: 1,
    }
    fetchAlgolia.mockReset()
  })

  function mockAlgolia({ hits, nbHits }) {
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: hits,
          nbHits: nbHits,
          nbPages: 0,
          page: 0,
        })
      }),
    )
  }

  it('should render two OfferTile when two offers', async () => {
    // given
    mockAlgolia({ hits: [offerOne, offerTwo], nbHits: 2 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )

    await wrapper.update()

    // then
    const offers = wrapper.find(Module).find(OfferTile)
    expect(offers).toHaveLength(2)
    const firstOffer = offers.at(0)
    expect(firstOffer.prop('hit')).toStrictEqual(offerOne)
    const secondOffer = offers.at(1)
    expect(secondOffer.prop('hit')).toStrictEqual(offerTwo)
  })

  it('should render a pane with a title', async () => {
    // given
    mockAlgolia({ hits: [offerOne], nbHits: 1 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const title = wrapper.find(Module).find({ children: 'Les offres près de chez toi!' })
    expect(title).toHaveLength(1)
  })

  it('should not render OfferTile nor pane title when no hits', async () => {
    mockAlgolia({ hits: [], nbHits: 0 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const offerTile = wrapper.find(Module).find(OfferTile)
    expect(offerTile).toHaveLength(0)
    const title = wrapper.find(Module).find({ children: 'Les offres près de chez toi!' })
    expect(title).toHaveLength(0)
  })

  it('should render a cover when provided', async () => {
    mockAlgolia({ hits: [offerOne], nbHits: 1 })
    const cover = 'https://www.link-to-my-image.com'
    props.module = new OffersWithCover({ algolia, cover, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const imageCover = wrapper.find(Module).find(`img[src="${cover}"]`)
    expect(imageCover).toHaveLength(1)
  })

  it('should not fetch algolia when geolocation parameters are null', async () => {
    algolia.isGeolocated = true
    const cover = 'https://www.link-to-my-image.com'
    props.geolocation = { latitude: null, longitude: null }
    props.module = new OffersWithCover({ algolia, cover, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    expect(fetchAlgolia).not.toHaveBeenCalled()
  })

  it('should not render OfferTile when two offers are retrieved but min offers is superior', async () => {
    // given
    mockAlgolia({ hits: [offerOne, offerTwo], nbHits: 2 })
    display.minOffers = 3
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )

    // then
    const offers = wrapper.find(Module).find(OfferTile)
    expect(offers).toHaveLength(0)
  })

  it('should render a see more tile when displayed offers hits are inferior to total of hits', async () => {
    // given
    mockAlgolia({ hits: [offerOne], nbHits: 5 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )

    await wrapper.update()

    // then
    const seeMore = wrapper.find(SeeMore)
    expect(seeMore).toHaveLength(1)
    expect(seeMore.props()).toStrictEqual({
      historyPush: props.historyPush,
      isSwitching: false,
      layout: "one-item-medium",
      parameters: {
        aroundRadius: null,
        beginningDatetime:null,
        endingDatetime:null,
        geolocation: {
          latitude: 1,
          longitude: 2,
        },
        hitsPerPage: 3,
        offerCategories: ["CINEMA", "LECON", "LIVRE"],
        offerIsDuo: true,
        offerIsFree: false,
        offerIsNew: true,
        offerTypes: { isDigital: false, isEvent: true, isThing: true },
        priceRange: [1, 10],
        searchAround: false,
        tags: [],
      },
    })
  })

  it('should not render a see more tile when displayed offers hits are equal to total of hits', async () => {
    mockAlgolia({ hits: [offerOne], nbHits: 1 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const seeMore = wrapper.find(SeeMore)
    expect(seeMore).toHaveLength(0)
  })

  it('should not render a see more tile when algolia parameters contains tags', async () => {
    algolia.tags = ["Offres de l'été"]
    mockAlgolia({ hits: [offerOne], nbHits: 5 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const seeMore = wrapper.find(SeeMore)
    expect(seeMore).toHaveLength(0)
  })

  it('should not render a see more tile when algolia parameters contains beginningDatetime', async () => {
    algolia.beginningDatetime = "2020-01-01T20:00:00"
    mockAlgolia({ hits: [offerOne], nbHits: 5 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const seeMore = wrapper.find(SeeMore)
    expect(seeMore).toHaveLength(0)
  })

  it('should not render a see more tile when algolia parameters contains endingDatetime', async () => {
    algolia.endingDatetime = "2020-01-01T20:00:00"
    mockAlgolia({ hits: [offerOne], nbHits: 5 })
    props.module = new Offers({ algolia, display })

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const seeMore = wrapper.find(SeeMore)
    expect(seeMore).toHaveLength(0)
  })

  describe('when layout is two tiles', () => {
    it('should render a cover, two offer tiles, a see more tile', async () => {
      // given
      mockAlgolia({ hits: [offerOne, offerTwo], nbHits: 3 })
      const cover = 'https://www.link-to-my-image.com'
      display.layout = PANE_LAYOUT['TWO-ITEMS']
      props.module = new OffersWithCover({ algolia, cover, display })

      // when
      const wrapper = await mount(
        <MemoryRouter>
          <Module {...props} />
        </MemoryRouter>,
      )
      await wrapper.update()

      // then
      const seeMore = wrapper.find(SeeMore)
      expect(seeMore).toHaveLength(1)
      const imageCover = wrapper.find(Module).find(`img[src="${cover}"]`)
      expect(imageCover).toHaveLength(1)
      const offerTiles = wrapper.find(OfferTile)
      expect(offerTiles).toHaveLength(2)
    })
  })
})
