import { mount } from 'enzyme'
import React from 'react'
import Home from '../Home'
import { Link } from 'react-router-dom'
import { MemoryRouter } from 'react-router'
import Icon from '../../../layout/Icon/Icon'
import { fetchHomepage } from '../../../../vendor/contentful/contentful'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import Module from '../Module/Module'
import Offers from '../domain/ValueObjects/Offers'
import BusinessPane from '../domain/ValueObjects/BusinessPane'
import BusinessModule from '../BusinessModule/BusinessModule'
import ExclusivityPane from '../domain/ValueObjects/ExclusivityPane'
import ExclusivityModule from '../ExclusivityModule/ExclusivityModule'
import { parse } from 'query-string'

jest.mock('../Module/domain/buildTiles', () => ({
  buildPairedTiles: jest.fn().mockReturnValue([]),
  buildTiles: jest.fn().mockReturnValue([]),
}))
jest.mock('query-string', () => ({
  parse: jest.fn(),
}))
jest.mock('../../../../vendor/contentful/contentful', () => ({
  fetchHomepage: jest.fn(),
}))
jest.mock('../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn().mockResolvedValue({ hits: [], nbHits: 5 }),
}))
jest.mock('../domain/parseAlgoliaParameters', () => ({
  parseAlgoliaParameters: jest.fn().mockReturnValue({}),
}))
describe('src | components | Home', () => {
  let props

  beforeEach(() => {
    fetchHomepage.mockResolvedValue([])
    parse.mockReturnValue({})
    props = {
      geolocation: {
        latitude: 5,
        longitude: 10,
      },
      history: {
        location: {
          search: '',
        },
        push: jest.fn(),
      },
      match: {},
      user: {
        publicName: 'Iron Man',
        wallet_balance: 200.1,
      },
    }
  })

  afterEach(() => {
    fetchHomepage.mockReset()
  })

  it('should render a Link component with the profil icon', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/profil')

    const icon = link.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-informations-white')
  })

  it('should render a title with the user public name', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )

    // then
    const title = wrapper.find({ children: 'Bonjour Iron Man' })
    expect(title).toHaveLength(1)
  })

  it('should render a subtitle with the user wallet balance', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )

    // then
    const title = wrapper.find({ children: 'Tu as 200,1 € sur ton pass' })
    expect(title).toHaveLength(1)
  })

  it('should render a module component when module is for offers with cover', async () => {
    // given
    const offersWithCover = new OffersWithCover({
      algolia: { isDuo: true },
      cover: 'my-cover',
      display: { layout: 'one-item-medium' },
    })
    fetchHomepage.mockResolvedValue([offersWithCover])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const moduleWithCover = wrapper.find(Module)
    expect(moduleWithCover).toHaveLength(1)
    expect(moduleWithCover.props()).toStrictEqual({
      geolocation: { latitude: 5, longitude: 10 },
      historyPush: expect.any(Function),
      module: offersWithCover,
      row: 0,
    })
  })

  it('should render a module component when module is for offers', async () => {
    // given
    const offers = new OffersWithCover({
      algolia: { isDuo: true },
      display: { layout: 'one-item-medium' },
    })
    fetchHomepage.mockResolvedValue([offers])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const module = wrapper.find(Module)
    expect(module).toHaveLength(1)
    expect(module.props()).toStrictEqual({
      geolocation: { latitude: 5, longitude: 10 },
      historyPush: expect.any(Function),
      module: offers,
      row: 0,
    })
  })

  it('should render a business module component when module is for business information', async () => {
    // given
    fetchHomepage.mockResolvedValue([
      new BusinessPane({
        image: 'my-image',
        title: 'my-title',
        url: 'my-url',
      }),
    ])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const module = wrapper.find(BusinessModule)
    expect(module).toHaveLength(1)
  })

  it('should render an exclusivity module component when module is for an exclusive offer', async () => {
    // given
    fetchHomepage.mockResolvedValue([
      new ExclusivityPane({
        alt: 'my alt text',
        image: 'https://www.link-to-my-image.com',
        offerId: 'AE',
      }),
    ])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    const module = wrapper.find(ExclusivityModule)
    expect(module).toHaveLength(1)
  })

  it('should fetch homepage using entry id from url when provided', async () => {
    // given
    const entryId = 'ABCDE'
    parse.mockReturnValue({ entryId })
    props.history.location.search = entryId
    fetchHomepage.mockResolvedValue([new Offers({})])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>,
    )
    await wrapper.update()

    // then
    expect(fetchHomepage).toHaveBeenCalledWith({ entryId })
  })
})
