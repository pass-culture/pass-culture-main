import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import { getStubStore } from '../../../../utils/stubStore'
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

  it('should render a profil page when navigating to /accueil/profil', async () => {
    // When
    const mockStore = getStubStore({
      currentUser: (
        state = new User({
          email: 'john.doe@example.fr',
          expenses: {
            all: { actual: 287, max: 500 },
            digital: { actual: 11, max: 200 },
            physical: { actual: 23, max: 200 },
          },
          firstName: 'PC Test Jeune',
          publicName: 'Iron Man',
          wallet_balance: 200.1,
        })
      ) => state,
      data: (
        state = {
          features: [],
          readRecommendations: [],
        }
      ) => state,
    })
    const wrapper = await mount(
      <Provider store={mockStore}>
        <MemoryRouter initialEntries={['/accueil/profil']}>
          <Home {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const profile = wrapper.find({ children: 'Informations personnelles' })
    expect(profile).toHaveLength(1)
  })

  it('should render the main view when navigating to /accueil', async () => {
    // Given
    const flushPromises = () => new Promise(setImmediate)
    const offersWithCover = new OffersWithCover({
      algolia: { isDuo: true },
      cover: 'my-cover',
      display: { title: 'Mon module', layout: 'one-item-medium', minOffers: 1 },
    })
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
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
      })
    )
    fetchHomepage.mockResolvedValue([offersWithCover])

    // When
    const wrapper = await mount(
      <MemoryRouter initialEntries={['/accueil']}>
        <Home {...props} />
      </MemoryRouter>
    )
    await flushPromises()
    wrapper.update()

    // Then
    const moduleName = wrapper.find('Module').find({ children: 'Mon module' })
    expect(moduleName).toHaveLength(1)
  })
})
