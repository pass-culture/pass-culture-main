import { shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'
import VenueProvidersManager from '../VenueProvidersManager'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  let props
  let createVenueProvider
  let loadProvidersAndVenueProviders
  let notify
  let history

  beforeEach(() => {
    createVenueProvider = jest.fn()
    loadProvidersAndVenueProviders = jest.fn()
    notify = jest.fn()
    history = {
      push: jest.fn()
    }
    props = {
      createVenueProvider,
      loadProvidersAndVenueProviders,
      notify,
      history,
      match: {
        params: {
          offererId: 'CC',
          venueId: 'AB',
          venueProviderId: 'AE'
        }
      },
      providers: [
        {id: 'DD', requireProviderIdentifier: true},
        {id: 'EE', requireProviderIdentifier: true}
      ],
      venue: {id: 'AB'},
      venueProviders: [{id: 'AA'}, {id: 'BB'}],
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<VenueProvidersManager {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should initialize VenueProvidersManager component with default state', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      expect(wrapper.state()).toEqual({
        isCreationMode: false,
        isLoadingMode: false,
        isProviderSelected: false,
        venueIdAtOfferProviderIsRequired: true
      })
    })

    it('should return is creation mode to true when query param "venueProviderId" is "nouveau"', () => {
      // given
      props.match.params.venueProviderId = 'nouveau'

      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      expect(wrapper.state()).toEqual({
        isCreationMode: true,
        isLoadingMode: false,
        isProviderSelected: false,
        venueIdAtOfferProviderIsRequired: true
      })
    })

    it('should contain a block with information regarding importation process', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      const title = wrapper.find('h2')
      expect(title).toBeDefined()
      const span = title.find('span')
      expect(span.text()).toBe('Si vous avez plusieurs comptes auprès de la même source, ajoutez-les successivement.')
    })

    it('should display 2 VenueProviderItemContainer when there are 2 venue providers', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      const venueProviderItemContainers = wrapper.find(VenueProviderItem)
      expect(venueProviderItemContainers).toHaveLength(2)
      expect(venueProviderItemContainers.at(0).prop('venueProvider')).toEqual({id: 'AA'})
      expect(venueProviderItemContainers.at(1).prop('venueProvider')).toEqual({id: 'BB'})
    })

    it('should retrieve providers and venue providers when component is mounted', () => {
      // when
      shallow(<VenueProvidersManager {...props} />)

      // then
      expect(loadProvidersAndVenueProviders).toHaveBeenCalled()
    })

    it('should update current URL when clicking on add venue provider button', () => {
      // given
      const wrapper = shallow(<VenueProvidersManager {...props} />)
      const addOfferBtn = wrapper.find('#add-venue-provider-btn')

      // when
      addOfferBtn.simulate('click')

      // then
      expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/AB/fournisseurs/nouveau')
    })

    it('should display an import button when at least one provider is given', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      const importButton = wrapper.find('#add-venue-provider-btn')
      expect(importButton).toHaveLength(1)
      expect(importButton.prop('className')).toBe('button is-secondary')
      expect(importButton.prop('disabled')).toBe(false)
      expect(importButton.prop('id')).toBe('add-venue-provider-btn')
      expect(importButton.prop('onClick')).toEqual(expect.any(Function))
      expect(importButton.prop('type')).toBe('button')
    })

    it('should not display an import button when no providers are given', () => {
      // given
      props.providers = []

      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      const importButton = wrapper.find('#add-venue-provider-btn')
      expect(importButton).toHaveLength(0)
    })
  })

  describe('handleSubmit', () => {
    it('should update venue provider using API', () => {
      // given
      const formValues = {
        id: 'AA',
        provider: '{"id": "CC"}',
        venueIdAtOfferProvider: 'BB'
      }
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // when
      wrapper.instance().handleSubmit(formValues, {})

      // then
      expect(wrapper.state('isLoadingMode')).toBe(true)
      expect(createVenueProvider).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        {providerId: 'CC', venueId: 'AA', venueIdAtOfferProvider: 'BB'}
      )
    })
  })

  describe('handleSuccess', () => {
    it('should update current url when action was handled successfully', () => {
      // given
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // when
      wrapper.instance().handleSuccess()

      // then
      expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/AB')
    })
  })

  describe('handleFail', () => {
    it('should display a notification with the proper informations', () => {
      // given
      const wrapper = shallow(<VenueProvidersManager {...props} />)
      const action = {
        payload: {
          errors: [{
            error: 'fake error'
          }]
        }
      }
      const form = {
        batch: jest.fn()
      }

      // when
      wrapper.instance().handleFail(form)({}, action)

      // then
      expect(notify).toHaveBeenCalledWith([{error: 'fake error'}])
    })

    it('should reset component state with the default values', () => {
      // given
      const wrapper = shallow(<VenueProvidersManager {...props} />)
      const action = {
        payload: {
          errors: [{
            error: 'fake error'
          }]
        }
      }
      const form = {
        batch: jest.fn()
      }

      // when
      wrapper.instance().handleFail(form)({}, action)

      // then
      expect(wrapper.state()).toEqual({
        isCreationMode: false,
        isLoadingMode: false,
        isProviderSelected: false,
        venueIdAtOfferProviderIsRequired: true
      })
    })
  })

  describe('handleChange', () => {
    let input
    let onChange

    beforeEach(() => {
      onChange = jest.fn()
      input = {
        onChange
      }
    })

    it('should update state values when selected option is valid and different from default value', () => {
      // given
      const event = {
        target: {
          value: '{"id":"AE", "requireProviderIdentifier": true}'
        }
      }
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // when
      wrapper.instance().handleChange(event, input)

      // then
      expect(wrapper.state('isProviderSelected')).toBe(true)
      expect(wrapper.state('venueIdAtOfferProviderIsRequired')).toBe(true)
    })

    it('should reset form state when selected option is equal to default value', () => {
      // given
      const event = {
        target: {
          value: '{"id":"default", "name": "Choix de la source"}'
        }
      }
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // when
      wrapper.instance().handleChange(event, input)

      // then
      expect(wrapper.state()).toEqual({
        isCreationMode: false,
        isLoadingMode: false,
        isProviderSelected: false,
        venueIdAtOfferProviderIsRequired: true
      })
    })
  })

  describe('form', () => {
    beforeEach(() => {
      props.match.params.venueProviderId = 'nouveau'
      props.venueProviders = []
    })

    it('should render form with the proper values using user input', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toBeDefined()
      expect(form.prop('decorators')).toEqual(expect.anything())
      expect(form.prop('initialValues')).toEqual({id: 'AB'})
      expect(form.prop('onSubmit')).toEqual(expect.any(Function))
      expect(form.prop('render')).toEqual(expect.any(Function))
    })
  })
})
