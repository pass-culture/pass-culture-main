import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import OfferTile from '../OfferTile'
import { Link } from 'react-router-dom'
import { DEFAULT_THUMB_URL } from '../../../../../../utils/thumb'
import { formatSearchResultDate } from '../../../../../../utils/date/date'

jest.mock('../../../../../../utils/date/date', () => ({
  formatSearchResultDate: jest.fn()
}))
describe('src | components | OfferTile', () => {
  let props

  beforeEach(() => {
    props = {
      hit: {
        offer: {
          dates: [],
          id: 'AE',
          isDuo: false,
          isEvent: false,
          name: 'Avengers - Age of Ultron',
          priceMin: 1,
          priceMax: 1,
          thumbUrl: 'my-thumb'
        },
        venue: {
          departementCode: '54',
          name: 'Librairie Kléber'
        }
      }
    }
  })

  it('should render an offer tile with a link', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/offre/details/AE')
  })

  it('should render an offer tile with an image when provided', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.prop('alt')).toBe("")
    expect(img.prop('src')).toBe('my-thumb')
  })

  it('should render an offer tile with default thumb when no image', () => {
    // given
    props.hit.offer.thumbUrl = null

    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.prop('src')).toBe(DEFAULT_THUMB_URL)
  })

  it('should render an offer tile with venue name', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const venue = wrapper.find({ children: 'Librairie Kléber' })
    expect(venue).toHaveLength(1)
  })

  it('should render an offer tile with the price', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const price = wrapper.find({ children: '1 €' })
    expect(price).toHaveLength(1)
  })

  it('should render an offer tile with dates when event', () => {
    // given
    const mockedDate = 'A partir du 8 juillet'
    props.hit.offer.dates = [1594300450]
    props.hit.offer.isEvent = true
    formatSearchResultDate.mockReturnValue(mockedDate)

    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const date = wrapper.find({ children: `${mockedDate} - ` })
    expect(date).toHaveLength(1)
  })

  it('should render an offer tile with the offer name', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <OfferTile {...props} />
      </MemoryRouter>
    )

    // then
    const offerName = wrapper.find({ children: 'Avengers - Age of Ultron' })
    expect(offerName).toHaveLength(1)
  })
})
