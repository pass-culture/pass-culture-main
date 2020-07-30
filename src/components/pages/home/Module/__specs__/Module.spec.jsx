import Offers from '../../domain/ValueObjects/Offers'
import { PANE_LAYOUT } from '../../domain/layout'
import { mount } from 'enzyme'
import Module from '../Module'
import React from 'react'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import { MemoryRouter } from 'react-router'
import OfferTile from '../OfferTile/OfferTile'
import OffersWithCover from '../../domain/ValueObjects/OffersWithCover'
import Icon from '../../../../layout/Icon/Icon'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('src | components | Module', () => {
  let algolia
  let display
  let offerOne
  let offerTwo
  let geolocation

  beforeEach(() => {
    algolia = {
      aroundRadius: null,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: ['CINEMA', 'LECON', 'LIVRE'],
      endingDatetime: '2020-07-15T00:00+02:00',
      hitsPerPage: 5,
      isDigital: false,
      isDuo: true,
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
      minOffers: 5,
      title: 'Les offres près de chez toi!',
    }
    geolocation = {
      latitude: 1,
      longitude: 2
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
    fetchAlgolia.mockReset()
  })

  it('should render two OfferTile when two offers', async () => {
    // given
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: [offerOne, offerTwo],
          nbHits: 0,
          nbPages: 0,
          page: 0,
        })
      })
    )

    const props = {
      geolocation,
      historyPush: jest.fn(),
      module: new Offers({
        algolia,
        display,
      }),
      row: 1,
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
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

  it('should render a pane with pane title', async () => {
    // given
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: [offerOne],
          nbHits: 0,
          nbPages: 0,
          page: 0,
        })
      })
    )

    const props = {
      geolocation,
      historyPush: jest.fn(),
      module: new Offers({
        algolia,
        display,
      }),
      row: 1,
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const title = wrapper.find(Module).find({ children: 'Les offres près de chez toi!' })
    expect(title).toHaveLength(1)
  })

  it('should not render OfferTile nor pane title when no hits', async () => {
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: [],
          nbHits: 0,
          nbPages: 0,
          page: 0,
        })
      })
    )

    const props = {
      geolocation,
      historyPush: jest.fn(),
      module: new Offers({
        algolia,
        display,
      }),
      row: 1,
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const offerTile = wrapper.find(Module).find(OfferTile)
    expect(offerTile).toHaveLength(0)
    const title = wrapper.find(Module).find({ children: 'Les offres près de chez toi!' })
    expect(title).toHaveLength(0)
  })

  it('should render a cover when provided', async () => {
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: [offerOne],
          nbHits: 0,
          nbPages: 0,
          page: 0,
        })
      })
    )

    const cover = 'https://www.link-to-my-image.com'
    const props = {
      geolocation,
      historyPush: jest.fn(),
      module: new OffersWithCover({
        algolia,
        cover,
        display,
      }),
      row: 1,
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const imageCover = wrapper.find(Module).find(`img[src="${cover}"]`)
    expect(imageCover).toHaveLength(1)
    const icon = wrapper.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-swipe-tile')
  })

  it('should not fetch algolia when parameters are null', async () => {
    algolia.isGeolocated = true
    geolocation = {
      latitude: null,
      longitude: null
    }
    const cover = 'https://www.link-to-my-image.com'
    const props = {
      geolocation,
      historyPush: jest.fn(),
      module: new OffersWithCover({
        algolia,
        cover,
        display,
      }),
      row: 1,
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    expect(fetchAlgolia).not.toHaveBeenCalled()
  })
})
