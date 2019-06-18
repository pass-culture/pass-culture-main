import { shallow } from 'enzyme'
import React from 'react'
import VenueProvidersManager, { FormRendered } from '../VenueProvidersManager'
import VenueProviderItemContainer from '../VenueProviderItem/VenueProviderItemContainer'
import { Form } from 'react-final-form'
import { HiddenField, TextField } from '../../../../layout/form/fields'
import { Icon } from '../../../../layout/Icon'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  let props
  let dispatch
  let history

  beforeEach(() => {
    dispatch = jest.fn()
    history = {
      push: jest.fn()
    }
    props = {
      dispatch,
      history,
      match: {
        params: {
          offererId: 'CC',
          venueId: 'AB',
          venueProviderId: 'AE'
        }
      },
      provider: {},
      providers: [{id: 'DD'}, {id: 'EE'}],
      venue: {id: 'AB'},
      venueProvider: {id: 'AE'},
      venueProviders: [{id: 'AA'}, {id: 'BB'}],
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<VenueProvidersManager {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
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
        selectedValue: 'default',
      })
    })

    describe('render', () => {
      it('should initialize component with default state', () => {
        // when
        const wrapper = shallow(<VenueProvidersManager {...props} />)

        // then
        expect(wrapper.state()).toEqual({
          isCreationMode: false,
          isLoadingMode: false,
          isProviderSelected: false,
          selectedValue: 'default'
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
        const venueProviderItemContainers = wrapper.find(VenueProviderItemContainer)
        expect(venueProviderItemContainers).toHaveLength(2)
        expect(venueProviderItemContainers.at(0).prop('venue')).toEqual({id: 'AB'})
        expect(venueProviderItemContainers.at(0).prop('venueProvider')).toEqual({id: 'AA'})
        expect(venueProviderItemContainers.at(1).prop('venue')).toEqual({id: 'AB'})
        expect(venueProviderItemContainers.at(1).prop('venueProvider')).toEqual({id: 'BB'})
      })

      it('should retrieve providers and venue providers when component is mounted', () => {
        // when
        shallow(<VenueProvidersManager {...props} />)

        // then
        expect(dispatch.mock.calls[0][0]).toEqual({
          config: {
            apiPath: '/providers',
            method: 'GET'
          },
          type: 'REQUEST_DATA_GET_/PROVIDERS'
        })
        expect(dispatch.mock.calls[1][0]).toEqual({
          config: {
            apiPath: '/venueProviders?venueId=AB',
            method: 'GET'
          },
          type: 'REQUEST_DATA_GET_/VENUEPROVIDERS?VENUEID=AB'
        })
      })

      it('should update is creation mode to true when clicking on add offer button', async () => {
        // given
        const wrapper = shallow(<VenueProvidersManager {...props} />)
        const addOfferBtn = wrapper.find('#add-offer-btn')

        // when
        addOfferBtn.simulate('click')

        // then
        expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/AB/fournisseurs/nouveau')
      })
    })

    describe('functions', () => {
      describe('handleSubmit', () => {
        it('should update venue provider using API', () => {
          // given
          const formValues = {
            venueId: 'AA',
            venueIdAtOfferProvider: 'BB'
          }
          const wrapper = shallow(<VenueProvidersManager {...props} />)
          wrapper.setState({selectedValue: {id: 'CC', name: 'fake value'}})

          // when
          wrapper.instance().handleSubmit(formValues)

          // then
          expect(wrapper.state('isLoadingMode')).toBe(true)
          expect(dispatch).toHaveBeenCalledWith({
            config: {
              apiPath: '/venueProviders',
              body: {
                providerId: 'CC',
                venueId: 'AA',
                venueIdAtOfferProvider: 'BB'
              },
              handleFail: expect.any(Function),
              handleSuccess: expect.any(Function),
              method: 'POST'
            },
            type: 'REQUEST_DATA_POST_/VENUEPROVIDERS'
          })
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

          // when
          wrapper.instance().handleFail()

          // then
          expect(dispatch).toHaveBeenCalledWith({
            patch: {
              text: 'Une erreur est survenue lors de l\'import.',
              type: 'fail'
            },
            type: 'SHOW_NOTIFICATION'
          })
        })

        it('should reset component state with the default values', () => {
          // given
          const wrapper = shallow(<VenueProvidersManager {...props} />)

          // when
          wrapper.instance().handleFail()

          // then
          expect(wrapper.state()).toEqual({
            isCreationMode: false,
            isLoadingMode: false,
            isProviderSelected: false,
            selectedValue: {
              id: 'default',
              name: 'Choix de la source'
            }
          })
        })
      })

      describe('handleChange', () => {
        it('should update state values when selected option is valid and different from default value', () => {
          // given
          const event = {
            target: {
              value: 'AE'
            }
          }
          const wrapper = shallow(<VenueProvidersManager {...props} />)

          // when
          wrapper.instance().handleChange(event)

          // then
          expect(wrapper.state('isProviderSelected')).toBe(true)
          expect(wrapper.state('selectedValue')).toEqual({id: 'AE'})
        })

        it('should reset form state when selected option is equal to default value', () => {
          // given
          const event = {
            target: {
              value: 'default'
            }
          }
          const wrapper = shallow(<VenueProvidersManager {...props} />)

          // when
          wrapper.instance().handleChange(event)

          // then
          expect(wrapper.state()).toEqual({
            isCreationMode: false,
            isLoadingMode: false,
            isProviderSelected: false,
            selectedValue: {id: 'default', name: "Choix de la source"}
          })
        })
      })
    })

    describe('form', () => {
      beforeEach(() => {
        props.match.params.venueProviderId = 'nouveau'
        props.venueProviders = []
      })

      it('should render form with the proper values from user input', async() => {
        // when
        const wrapper = shallow(<VenueProvidersManager {...props} />)

        // then
        const form = wrapper.find(Form)
        expect(form).toBeDefined()
        expect(form.prop('onSubmit')).toEqual(expect.any(Function))
        expect(form.prop('initialValues')).toEqual({id: 'AE'})
        expect(form.prop('render')).toEqual(expect.any(Function))
      })

      describe('rendered form', () => {
        let props
        let handleSubmit
        let handleChange

        beforeEach(() => {
          handleSubmit = jest.fn()
          handleChange = jest.fn()
          props = {
            providers: [{id: 'AA'}, {id: 'BB'}],
            isProviderSelected: false,
            isLoadingMode: false,
            isCreationMode: false,
            selectedValue: {
              name: 'Open Agenda'
            },
            handleChange,
            handleSubmit
          }
        })

        it('should render a HiddenField component with the right props', () => {
          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const hiddenField = renderedForm.find(HiddenField)
          expect(hiddenField).toBeDefined()
          expect(hiddenField.prop('name')).toBe('venueId')
        })

        it('should render a TextField component with the right props when provider is selected and not in loading mode', () => {
          // given
          props.isProviderSelected = true

          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const textField = renderedForm.find(TextField)
          expect(textField).toHaveLength(1)
          expect(textField.prop('className')).toBe('field-text fs12')
          expect(textField.prop('label')).toBe('Compte : ')
          expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
          expect(textField.prop('readOnly')).toBe(false)
          expect(textField.prop('required')).toBe(true)
        })

        it('should render a TextField component with the right props when provider is selected and in loading mode', () => {
          // given
          props.isProviderSelected = true
          props.isLoadingMode = true

          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const textField = renderedForm.find(TextField)
          expect(textField).toHaveLength(1)
          expect(textField.prop('className')).toBe('field-text fs12 field-is-read-only')
          expect(textField.prop('label')).toBe('Compte : ')
          expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
          expect(textField.prop('readOnly')).toBe(true)
          expect(textField.prop('required')).toBe(true)
        })

        it('should display a message information when importing data', () => {
          // given
          props.isProviderSelected = true
          props.isLoadingMode = true

          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const importLabelContainer = renderedForm.find('.import-label-container')
          const importLabelSpan = importLabelContainer.find('span')
          expect(importLabelContainer).toHaveLength(1)
          expect(importLabelSpan).toHaveLength(1)
          expect(importLabelSpan.text()).toBe('Importation en cours. Cette étape peut durer plusieurs dizaines de minutes.')
        })

        it('should display a tooltip and an Icon component when provider is selected and not in loading mode', () => {
          // given
          props.isProviderSelected = true
          props.isLoadingMode = false

          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const tooltip = renderedForm.find('.tooltip-info')
          expect(tooltip).toHaveLength(1)
          expect(tooltip.prop('className')).toBe('button tooltip tooltip-info')
          expect(tooltip.prop('data-place')).toBe('bottom')
          expect(tooltip.prop('data-tip')).toBe("<p>Veuillez saisir un identifiant.</p>")
          const icon = tooltip.find(Icon)
          expect(icon).toHaveLength(1)
          expect(icon.prop('svg')).toBe('picto-info')
        })

        it('should display an import button when provider is selected and in creation mode and not in loading mode', () => {
          // given
          props.isProviderSelected = true
          props.isCreationMode = true
          props.isLoadingMode = false

          // when
          const renderedForm = shallow(FormRendered({...props})(handleSubmit))

          // then
          const importButtonContainer = renderedForm.find('.button-provider-import-container')
          expect(importButtonContainer).toHaveLength(1)
          const importButton = importButtonContainer.find('button')
          expect(importButton).toHaveLength(1)
          expect(importButton.prop('className')).toBe('button is-intermediate button-provider-import')
          expect(importButton.prop('type')).toBe('submit')
          expect(importButton.text()).toBe('Importer')
        })
      })
    })
  })
})
