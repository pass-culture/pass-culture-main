import { render, screen, fireEvent } from '@testing-library/react'
import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from 'utils/stubStore'
import { fetchAllVenuesByProUser } from 'services/venuesService'
import { ALL_OFFERS, ALL_VENUES, ALL_VENUES_OPTION, DEFAULT_PAGE } from '../_constants'
import Offers from '../Offers'

const mountOffers = (props, store) => {
  return mount(
    <Provider store={store}>
      <MemoryRouter>
        <Offers {...props} />
      </MemoryRouter>
    </Provider>
  )
}

const renderOffer = (props, store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Offers {...props} />
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('../../../../services/venuesService', () => ({
  fetchAllVenuesByProUser: jest.fn(),
}))
describe('src | components | pages | Offers | Offers', () => {
  let change
  let parse
  let props
  let currentUser
  let store
  const proVenues = [
    {
      id: 'JI',
      name: 'Ma venue',
      offererName: 'Mon offerer',
      isVirtual: false,
    },
    {
      id: 'JQ',
      name: 'Ma venue virtuelle',
      offererName: 'Mon offerer',
      isVirtual: true,
    },
  ]

  beforeEach(() => {
    change = jest.fn()
    parse = jest.fn().mockReturnValue({})
    currentUser = { id: 'EY', isAdmin: false, name: 'Current User', publicName: 'USER' }
    store = getStubStore({
      data: (
        state = {
          offerers: [],
          users: [currentUser],
          venues: [{ id: 'JI', name: 'Venue' }],
        }
      ) => state,
      modal: (
        state = {
          config: {},
        }
      ) => state,
      offers: (
        state = {
          searchFilters: {},
        }
      ) => state,
    })

    props = {
      closeNotification: jest.fn(),
      currentUser,
      handleOnActivateAllVenueOffersClick: jest.fn(),
      handleOnDeactivateAllVenueOffersClick: jest.fn(),
      loadOffers: jest.fn().mockResolvedValue({ page: 1, pageCount: 2, offersCount: 5 }),
      loadTypes: jest.fn(),
      saveSearchFilters: jest.fn(),
      offers: [
        {
          id: 'N9',
          venueId: 'JI',
        },
      ],
      query: {
        change,
        parse,
      },
      types: [],
      venue: { name: 'Ma Venue', id: 'JI' },
    }
    fetchAllVenuesByProUser.mockResolvedValue(proVenues)
  })

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  describe('render', () => {
    it('should load offers from API with defaults props', () => {
      // When
      mountOffers(props, store)

      // Then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should display column titles when offers are returned', async () => {
      // Given
      props.offers = [{ id: 'KE', availabilityMessage: 'Pas de stock', venueId: 'JI' }]

      // When
      const wrapper = await mountOffers(props, store)

      // Then
      wrapper.update()
      const venueColumn = wrapper.find('th').find({ children: 'Lieu' })
      const stockColumn = wrapper.find('th').find({ children: 'Stock' })
      expect(venueColumn).toHaveLength(1)
      expect(stockColumn).toHaveLength(1)
    })

    it('should not display column titles when no offers are returned', async () => {
      // Given
      props.offers = []

      // When
      const wrapper = await mountOffers(props, store)

      // Then
      wrapper.update()
      const venueColumn = wrapper.find('th').find({ children: 'Lieu' })
      const stockColumn = wrapper.find('th').find({ children: 'Stock' })
      expect(venueColumn).toHaveLength(0)
      expect(stockColumn).toHaveLength(0)
    })

    it('should render as much offers as given in props', async () => {
      // Given
      props.offers = [
        {
          id: 'M4',
          isActive: true,
          isEditable: true,
          isFullyBooked: false,
          isEvent: true,
          isThing: false,
          hasBookingLimitDatetimesPassed: false,
          name: 'My little offer',
          thumbUrl: '/my-fake-thumb',
          venueId: 'JI',
        },
        {
          id: 'AE3',
          isActive: true,
          isEditable: true,
          isFullyBooked: true,
          isEvent: false,
          isThing: true,
          hasBookingLimitDatetimesPassed: false,
          name: 'My other offer',
          thumbUrl: '/my-other-fake-thumb',
          venueId: 'JI',
        },
      ]

      // When
      const wrapper = await mountOffers(props, store)

      // Then
      wrapper.update()
      const firstOfferItem = wrapper.find({ children: 'My little offer' }).first()
      const secondOfferItem = wrapper.find({ children: 'My other offer' }).first()
      expect(firstOfferItem).toHaveLength(1)
      expect(secondOfferItem).toHaveLength(1)
    })

    describe('total number of offers', () => {
      it('should display total number of offers in plural if multiple offers', async () => {
        // Given
        const page = 1
        const pageCount = 2
        const offersCount = 17
        props.loadOffers.mockResolvedValueOnce({ page, pageCount, offersCount })

        // When
        const wrapper = await mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        // Then
        wrapper.update()
        const offersCounter = wrapper.find({ children: '17 offres' })
        expect(offersCounter).toHaveLength(1)
      })

      it('should display total number of offers in singular if one or no offer', async () => {
        // Given
        const page = 1
        const pageCount = 1
        const offersCount = 1
        props.loadOffers.mockResolvedValueOnce({ page, pageCount, offersCount })

        // When
        const wrapper = await mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        // Then
        wrapper.update()
        const offersCounter = wrapper.find({ children: '1 offre' })
        expect(offersCounter).toHaveLength(1)
      })
    })

    describe('filters', () => {
      it('should render venue filter with default option and given venues', async () => {
        // When
        const wrapper = await mountOffers(props, store)

        // Then
        wrapper.update()
        const venueSelect = wrapper.find('select[name="lieu"]')
        expect(venueSelect.props().value).toBe(ALL_VENUES_OPTION.id)
        const options = venueSelect.find('option')
        expect(options).toHaveLength(3)
        expect(options.at(0).text()).toBe(ALL_VENUES_OPTION.displayName)
        expect(options.at(1).text()).toBe(proVenues[0].name)
        expect(options.at(2).text()).toBe(`${proVenues[1].offererName} - Offre numérique`)
      })

      it('should render venue filter with given venue selected', async () => {
        // Given
        jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: proVenues[0].id })

        // When
        const wrapper = await mountOffers(props, store)

        // Then
        wrapper.update()
        const venueSelect = wrapper.find('select[name="lieu"]')
        expect(venueSelect.props().value).toBe(proVenues[0].id)
      })
    })
  })

  describe('on click on search button', () => {
    it('should load offers with default filters when no changes where made', () => {
      // Given
      const wrapper = mountOffers(props, store)
      const launchSearchButton = wrapper.find('form')

      // When
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should load offers with written offer name filter', () => {
      // Given
      const wrapper = mountOffers(props, store)
      const offerNameInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      offerNameInput.invoke('onChange')({ target: { value: 'Any word' } })

      // When
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: 'Any word',
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should load offers with selected venue filter', () => {
      // Given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: proVenues[0].id } })

      // When
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: proVenues[0].id,
      })
    })
  })

  describe('button to create an offer', () => {
    it('should not be displayed when user is an admin', () => {
      // Given
      props.currentUser.isAdmin = true

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const navLink = wrapper.find({ children: 'Créer une offre' })
      expect(navLink).toHaveLength(0)
    })

    it('should be displayed when user is not an admin', () => {
      // Given
      props.currentUser.isAdmin = false

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const offerCreationLink = wrapper.find({ children: 'Créer une offre' }).parent()
      expect(offerCreationLink).toHaveLength(1)
      expect(offerCreationLink.prop('href')).toBe('/offres/creation')
    })
  })

  describe('deactivate all offers from a venue', () => {
    it('should be displayed when offers and venue are given', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })
      expect(deactivateButton).toHaveLength(1)
    })

    it('should not be displayed when venue is missing', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: undefined })

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })
      expect(deactivateButton).toHaveLength(0)
    })

    it('should not be displayed when offers are missing', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })
      props.offers = []

      // When
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>
      )

      // Then
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })
      expect(deactivateButton).toHaveLength(0)
    })

    it('should send a request to api when clicked', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // Given
      const wrapper = mountOffers(props, store)

      // When
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })
      deactivateButton.simulate('click')

      // Then
      expect(props.handleOnDeactivateAllVenueOffersClick).toHaveBeenCalledWith('GY')
    })
  })

  describe('activate all offers from a venue', () => {
    it('should be displayed when offers and venue are given', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })
      expect(activateButton).toHaveLength(1)
    })

    it('should not be displayed when venue is missing', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: undefined })

      // When
      const wrapper = mountOffers(props, store)

      // Then
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })
      expect(activateButton).toHaveLength(0)
    })

    it('should not be displayed when offers are missing', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })
      props.offers = []

      // When
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>
      )

      // Then
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })
      expect(activateButton).toHaveLength(0)
    })

    it('should send a request to api when clicked', () => {
      // Given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      const wrapper = mountOffers(props, store)
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })

      // When
      activateButton.simulate('click')

      // Then
      expect(props.handleOnActivateAllVenueOffersClick).toHaveBeenCalledWith('GY')
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // Then
      wrapper.update()
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: 2,
      })
    })

    it('should have page value be removed when page value is first page', async () => {
      // Given
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')
      const leftArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')
      rightArrow.invoke('onClick')()

      // When
      leftArrow.invoke('onClick')()

      // Then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      // Given
      const wrapper = mountOffers(props, store)
      const searchInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      searchInput.invoke('onChange')({ target: { value: 'AnyWord' } })

      // When
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      wrapper.update()
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: 'AnyWord',
        page: null,
      })
    })

    it('should store search value', () => {
      // Given
      renderOffer(props, store)
      const searchInput = screen.getByPlaceholderText('Rechercher par nom d’offre')

      // When
      fireEvent.change(searchInput, { target: { value: 'search string' } })
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(props.saveSearchFilters).toHaveBeenCalledWith({
        venueId: ALL_VENUES,
        name: 'search string',
        page: DEFAULT_PAGE,
      })
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      // Given
      const wrapper = mountOffers(props, store)
      const searchInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      searchInput.invoke('onChange')({ target: { value: ALL_OFFERS } })

      // When
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })

    it('should have venue value when user filter by venue', async () => {
      // Given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: proVenues[0].id } })

      // When
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: proVenues[0].id,
        nom: null,
        page: null,
      })
    })

    it('should have venue value be removed when user ask for all venues', async () => {
      // Given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: ALL_VENUES } })

      // When
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // Then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })
  })

  describe('when leaving page', () => {
    it('should close offers activation / deactivation notification', () => {
      // Given
      props = {
        ...props,
        closeNotification: jest.fn(),
        notification: {
          tag: 'offers-activation',
        },
      }
      const wrapper = mountOffers(props, store)

      // When
      wrapper.unmount()

      // Then
      expect(props.closeNotification).toHaveBeenCalledWith()
    })

    it('should not fail on null notification', () => {
      // Given
      props = {
        ...props,
        closeNotification: jest.fn(),
        notification: null,
      }
      const wrapper = mountOffers(props, store)

      // When
      wrapper.unmount()

      // Then
      expect(props.closeNotification).not.toHaveBeenCalledWith()
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 1, pageCount: 4, offersCount: 5 })
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // Then
      expect(props.loadOffers).toHaveBeenLastCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: 2,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })

      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // Then
      expect(props.loadOffers).toHaveBeenLastCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should not be able to click on previous arrow when being on the first page', async () => {
      // Given
      props.query.parse.mockReturnValue({ page: DEFAULT_PAGE })

      // When
      const wrapper = await mountOffers(props, store)

      // Then
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')
      expect(rightArrow.prop('disabled')).toBe(true)
    })

    it('should not be able to click on next arrow when being on the last page', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })

      // When
      const wrapper = await mountOffers(props, store)

      // Then
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')
      expect(rightArrow.prop('disabled')).toBe(true)
    })
  })
})
