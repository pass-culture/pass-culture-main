import { mount } from 'enzyme'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'
import { campaignTracker } from '../../../../tracking/mediaCampaignsTracking'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { fetchHomepage } from '../../../../vendor/contentful/contentful'
import Home from '../Home'
import OffersWithCover from '../MainView/domain/ValueObjects/OffersWithCover'
import User from '../Profile/ValueObjects/User'

jest.mock('../../../../vendor/contentful/contentful', () => ({
  fetchHomepage: jest.fn(),
}))
jest.mock('../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
jest.mock('../../../../notifications/setUpBatchSDK', () => ({
  setCustomUserId: jest.fn(),
}))

const flushPromises = () => new Promise(setImmediate)

describe('src | components | home', () => {
  let props
  beforeEach(() => {
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
      match: {
        path: '/accueil',
      },
      trackAllModulesSeen: jest.fn(),
      trackAllTilesSeen: jest.fn(),
      updateCurrentUser: jest.fn(),
      user: new User({
        email: 'john.doe@example.fr',
        expenses: {
          all: { actual: 287, max: 500 },
          digital: { actual: 11, max: 200 },
          physical: { actual: 23, max: 200 },
        },
        firstName: 'PC Test Jeune',
        publicName: 'Iron Man',
        wallet_balance: 200.1,
      }),
    }
  })

  afterEach(jest.clearAllMocks)

  it('should show loading screen while waiting for geolocation', async () => {
    // Given
    fetchAlgolia.mockResolvedValue({
      hits: [],
      nbHits: 0,
      nbPages: 1,
      page: 1,
    })
    fetchHomepage.mockResolvedValue([])

    // When
    const wrapper = mount(
      <MemoryRouter initialEntries={['/accueil']}>
        <Home {...props} />
      </MemoryRouter>
    )
    await act(async () => {
      await flushPromises()
    })

    // Then
    const loadingScreen = wrapper.find({ children: 'Chargement en cours…' })
    expect(loadingScreen).toHaveLength(1)
  })

  it('should render the main view with a valid geolocation prop', async () => {
    // Given
    fetchAlgolia.mockResolvedValue({
      hits: [],
      nbHits: 0,
      nbPages: 1,
      page: 1,
    })
    fetchHomepage.mockResolvedValue([])

    // When
    const wrapper = mount(
      <MemoryRouter initialEntries={['/accueil']}>
        <Home {...props} />
      </MemoryRouter>
    )
    await act(async () => {
      await flushPromises()
      wrapper.update()
    })

    // Then
    const mainView = wrapper.find('MainView')
    expect(mainView.prop('geolocation')).toStrictEqual(props.geolocation)
  })

  it('should render the main view when navigating to /accueil', async () => {
    // Given
    const offersWithCover = new OffersWithCover({
      algolia: { isDuo: true },
      cover: 'my-cover',
      display: { title: 'Mon module', layout: 'one-item-medium', minOffers: 1 },
    })
    fetchAlgolia.mockResolvedValue({
      hits: [
        {
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
        },
      ],
      nbHits: 1,
      nbPages: 1,
      page: 1,
    })
    fetchHomepage.mockResolvedValue([offersWithCover])

    // When
    const wrapper = mount(
      <MemoryRouter initialEntries={['/accueil']}>
        <Home {...props} />
      </MemoryRouter>
    )

    // Then
    await act(async () => {
      await flushPromises()
      wrapper.update()
    })
    const moduleName = wrapper.find('Module').find({ children: 'Mon module' })
    expect(moduleName).toHaveLength(1)
  })

  it('should call media campaign tracker on mount only', async () => {
    // Given
    fetchAlgolia.mockResolvedValue({
      hits: [],
      nbHits: 0,
      nbPages: 1,
      page: 1,
    })
    fetchHomepage.mockResolvedValue([])

    // When mount
    const wrapper = mount(
      <MemoryRouter initialEntries={['/accueil']}>
        <Home {...props} />
      </MemoryRouter>
    )
    await act(async () => {
      await flushPromises()
      wrapper.update()
    })

    // Then
    expect(campaignTracker.home).toHaveBeenCalledTimes(1)

    // when rerender
    wrapper.setProps({})
    await act(async () => {
      await flushPromises()
      wrapper.update()
    })

    // Then
    expect(campaignTracker.home).toHaveBeenCalledTimes(1)
  })
})
