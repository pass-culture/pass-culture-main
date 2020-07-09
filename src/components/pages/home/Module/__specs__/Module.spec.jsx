import Offers from '../../domain/ValueObjects/Offers'
import { PANE_LAYOUT } from '../../domain/layout'
import { mount } from 'enzyme'
import Module from '../Module'
import React from 'react'
import { Link } from 'react-router-dom'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import { MemoryRouter } from 'react-router'
import { DEFAULT_THUMB_URL } from '../../../../../utils/thumb'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('src | components | Module', () => {
  let algolia
  let display
  let offerOne
  let offerTwo

  beforeEach(() => {
    algolia = {
      aroundRadius: 10000,
      beginningDatetime: '2020-07-10T00:00+02:00',
      categories: ['CINEMA', 'LECON', 'LIVRE'],
      endingDatetime: '2020-07-15T00:00+02:00',
      isDigital: false,
      isDuo: true,
      isEvent: true,
      isGeolocated: true,
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
  })

  it('should render two panes with two offers image and link to details', async () => {
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
      module: new Offers({
        algolia,
        display,
      }),
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )

    await wrapper.update()

    // then
    const offers = wrapper.find(Module).find('li')
    expect(offers).toHaveLength(2)
    const firstOffer = offers.at(0).find(Link)
    expect(firstOffer).toHaveLength(1)
    expect(firstOffer.prop('to')).toBe('/offre/details/NE')
    const firstOfferImage = firstOffer.find('img')
    expect(firstOfferImage).toHaveLength(1)
    expect(firstOfferImage.prop('src')).toBe('http://localhost/storage/thumbs/mediations/KQ')
    const secondOffer = offers.at(1).find(Link)
    expect(secondOffer).toHaveLength(1)
    const secondOfferImage = secondOffer.find('img')
    expect(secondOfferImage).toHaveLength(1)
    expect(secondOfferImage.prop('src')).toBe('http://localhost/storage/thumbs/mediations/PP')
    expect(secondOffer.prop('to')).toBe('/offre/details/AE')
  })

  it('should render a pane with one offer default image when no thumb', async () => {
    // given
    offerOne.offer.thumbUrl = null
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
      module: new Offers({
        algolia,
        display,
      }),
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )

    await wrapper.update()

    // then
    const offers = wrapper.find(Module).find('li')
    const firstOffer = offers.at(0).find(Link)
    const firstOfferImage = firstOffer.find('img')
    expect(firstOfferImage.prop('src')).toBe(DEFAULT_THUMB_URL)
  })

  it('should render a pane with venue name', async () => {
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
      module: new Offers({
        algolia,
        display,
      }),
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const offers = wrapper.find(Module).find('li')
    const firstOffer = offers.at(0).find(Link)
    const firstOfferVenueName = firstOffer.find({ children: 'Le Sous-sol'})
    expect(firstOfferVenueName).toHaveLength(1)
  })

  it('should render a pane with offer price', async () => {
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
      module: new Offers({
        algolia,
        display,
      }),
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const offers = wrapper.find(Module).find('li')
    const firstOffer = offers.at(0).find(Link)
    const firstOfferPrice = firstOffer.find({ children: '33 €'})
    expect(firstOfferPrice).toHaveLength(1)
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
      module: new Offers({
        algolia,
        display,
      }),
    }

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Module {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const title = wrapper.find(Module).find({ children : 'Les offres près de chez toi!'})
    expect(title).toHaveLength(1)
  })
})
