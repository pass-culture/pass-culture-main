import React from 'react'
import { shallow } from 'enzyme'
import { Field, Form } from 'pass-culture-shared'

import Offer from '../Offer'
import MediationsManager from '../MediationsManager/MediationsManagerContainer'
import HeroSection from '../../../layout/HeroSection/HeroSection'
import LocalProviderInformation from '../LocalProviderInformation/LocalProviderInformationContainer'

describe('src | components | pages | Offer | Offer ', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      currentUser: {
        isAdmin: false,
      },
      dispatch: dispatch,
      formInitialValues: {
        isDuo: false,
      },
      isEditableOffer: true,
      loadVenue: jest.fn(),
      location: {
        search: '?lieu=AQ',
      },
      match: {
        params: {
          offerId: 'creation',
        },
      },
      mergeOfferError: jest.fn(),
      query: {
        change: () => ({}),
        changeToReadOnly: () => ({}),
        context: () => ({}),
        parse: () => ({ lieu: 'AQ' }),
        translate: () => ({ venue: 'AQ ' }),
      },
      selectedOfferType: {},
      offer: {
        name: 'Super Livre',
        lastProvider: null,
      },
      history: {},
      trackCreateOffer: jest.fn(),
      trackModifyOffer: jest.fn(),
      venuesMatchingOfferType: [],
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Offer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleSuccess', () => {
    describe('when the offer is successfully modified', () => {
      it('should redirect to offer page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()

        props.match.params = {}
        props.query.changeToReadOnly = queryChangeToReadOnly

        const wrapper = shallow(<Offer {...props} />)

        // when
        const queryParams = { gestion: '' }
        const offer = { id: 'SN' }
        const action = {
          config: { method: 'PATCH' },
          payload: { datum: offer },
        }
        wrapper.instance().onHandleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })

    describe('when the offer is successfully modified (réécrire)', () => {
      it('should redirect to gestion page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'creation',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          isEditableOffer: true,
          formInitialValues: {
            isDuo: false,
          },
          query: {
            changeToReadOnly: queryChangeToReadOnly,
            context: () => ({}),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ ' }),
          },
          dispatch: dispatch,
          history: {},
          selectedOfferType: {},
          trackCreateOffer: jest.fn(),
          trackModifyOffer: jest.fn(),
        }

        const wrapper = shallow(<Offer {...initialProps} />)

        // when
        const queryParams = { gestion: '' }
        const offer = { id: 'SN' }
        const action = { config: { method: 'POST' }, payload: { datum: offer } }
        wrapper.instance().onHandleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })
  })

  describe('isNational', () => {
    it('should display isNational if admin user', () => {
      // given
      props.currentUser.isAdmin = true
      const wrapper = shallow(<Offer {...props} />)

      // when
      const result = wrapper.find(Field).find('[name="isNational"]')

      // then
      expect(result.prop('label')).toBe('Rayonnement national')
    })
  })

  describe('hasConditionalField', () => {
    it('should return false without selected offer type', () => {
      // given
      props.selectedOfferType = undefined
      const wrapper = shallow(<Offer {...props} />)

      // when
      const result = wrapper.instance().hasConditionalField(null)

      // then
      expect(result).toBe(false)
    })

    describe('when offer type is a subscription on show', () => {
      it('should show event type', () => {
        // given
        props.selectedOfferType = {
          value: 'ThingType.SPECTACLE_VIVANT_ABO',
        }
        const wrapper = shallow(<Offer {...props} />)

        // when
        const result = wrapper.instance().hasConditionalField('showType')

        // then
        expect(result).toBe(true)
      })
    })
  })

  describe('render', () => {
    describe('mediationsManager', () => {
      it("should be displayed when it's not a new offer", () => {
        // given
        props.match.params.offerId = 'N9'
        props.offer = {
          bookingEmail: 'fake@email.com',
          dateCreated: '2019-03-29T15:38:23.806900Z',
          dateModifiedAtLastProvider: '2019-03-29T15:38:23.806874Z',
          id: 'N9',
          idAtProviders: null,
          isActive: true,
          isDuo: false,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          lastProvider: null,
          modelName: 'Offer',
          productId: '94',
          venueId: 'AQ',
        }

        // when
        const wrapper = shallow(<Offer {...props} />)
        const mediationsManagerComponent = wrapper.find(MediationsManager)

        // then
        expect(mediationsManagerComponent).toHaveLength(1)
      })
    })

    describe('when creating a new offer', () => {
      it('should create a new Product when no offer type', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers')
      })

      it('should create a new Event when event type given', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        props.selectedOfferType = {
          type: 'Event',
        }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers')
      })

      it('should not display preview link', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        props.selectedOfferType = {
          type: 'Event',
        }
        const wrapper = shallow(<Offer {...props} />)

        // when
        const preview_section = wrapper.find(HeroSection)
        const preview_link = preview_section.find('OfferPreviewLink')

        // then
        expect(preview_link).toHaveLength(0)
      })

      describe('when the offer is an Event', () => {
        it('should allow to set an event duration', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Event',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const fieldGroups = wrapper.find('.field-group')
          const fieldGroupForUsefulInformation = fieldGroups.at(2)
          const durationField = fieldGroupForUsefulInformation.find(Field).at(0)
          expect(fieldGroups).toHaveLength(4)
          expect(durationField.prop('name')).toStrictEqual('durationMinutes')
        })

        it('should allow to configure the offer as DUO', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          const wrapper = shallow(<Offer {...props} />)

          // when
          const isDuoCheckbox = wrapper.find('#isDuo')

          // then
          expect(isDuoCheckbox).toHaveLength(1)
          expect(isDuoCheckbox.prop('type')).toStrictEqual('checkbox')
        })
      })

      describe('when the offer is a Thing', () => {
        it('should have a bookingEmail', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Thing',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const fieldGroups = wrapper.find('.field-group')
          const fieldGroupForUsefulInformation = fieldGroups.at(2)
          const bookingEmailField = fieldGroupForUsefulInformation.find(Field).at(0)
          expect(fieldGroups).toHaveLength(4)
          expect(bookingEmailField.prop('name')).toStrictEqual('bookingEmail')
        })

        it('should not have the duo option', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Thing',
          }
          const wrapper = shallow(<Offer {...props} />)

          // when
          const isDuoCheckbox = wrapper.find('#isDuo')

          // then
          expect(isDuoCheckbox).toHaveLength(0)
        })
      })

      describe('when the offer is digital only and selected venue is virtual', () => {
        it('should display an information insert', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            offlineOnly: false,
            onlineOnly: true,
            value: 'ThingType.JEUX_VIDEO',
          }

          props.venue = {
            isVirtual: true,
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then

          const warningText = wrapper.find('.yellow-insert > p').text()
          expect(warningText).toStrictEqual(
            "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
          )
          const insertLink = wrapper.find('.yellow-insert a')
          expect(insertLink.prop('href')).toStrictEqual(
            'https://docs.passculture.app/textes-normatifs'
          )
        })
      })

      describe('when the offer is digital only selected venue is virtual', () => {
        it('should not display a warning message about reimbursement of digital offers', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            offlineOnly: false,
            onlineOnly: true,
            value: 'ThingType.CINEMA_CARD',
          }

          props.venue = {
            isVirtual: true,
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const insert = wrapper.find('.yellow-insert')
          expect(insert).toHaveLength(0)
        })
      })
    })

    describe('when updating the offer', () => {
      it('should update a product when no offer type', () => {
        // given
        props.match.params = {
          offerId: 'VAG',
        }
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.offer = {
          id: 'VAG',
          productId: 'V24',
          lastProvider: {
            name: 'Open Agenda',
          },
        }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
      })

      it('should create a new Event when event type given', () => {
        // given
        props.match.params = {
          offerId: 'VAG',
        }
        props.selectedOfferType = {
          type: 'Event',
        }
        props.offer = {
          id: 'VAG',
          mediationId: 'TR',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          lastProvider: null,
        }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
      })

      it('should display preview link', () => {
        // given
        props.match.params = {
          offerId: 'VAG',
        }
        props.selectedOfferType = {
          type: 'Event',
        }
        props.offer = {
          id: 'VAG',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          lastProvider: null,
          activeMediation: {
            id: 'MED',
            isActive: true,
          },
          mediationsIds: ['MED'],
        }
        const wrapper = shallow(<Offer {...props} />)

        // when
        const preview_section = wrapper.find(HeroSection)

        // then
        const preview_link = preview_section.find('OfferPreviewLink')
        expect(preview_link.prop('href')).toMatch('/offre/details/VAG/MED')
      })
    })

    describe('display venue informations', () => {
      it('should display venue name when venue publicName is not provided', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        props.venuesMatchingOfferType = [{ name: 'quel beau théâtre' }, { name: 'quel beau musée' }]
        const expectedOptions = [{ name: 'quel beau théâtre' }, { name: 'quel beau musée' }]

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformation = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformation.find(Field).at(1)
        expect(fieldGroups).toHaveLength(4)
        expect(venueField.prop('options')).toStrictEqual(expectedOptions)
      })

      it('should display venue public name when venue public name is provided', () => {
        // given
        props.venuesMatchingOfferType = [
          { name: 'quel beau théâtre', publicName: 'quel beau théâtre public' },
          { name: 'quel beau musée', publicName: 'quel beau musée public' },
        ]
        const expectedOptions = [
          {
            name: 'quel beau théâtre public',
            publicName: 'quel beau théâtre public',
          },
          {
            name: 'quel beau musée public',
            publicName: 'quel beau musée public',
          },
        ]

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformation = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformation.find(Field).at(1)
        expect(fieldGroups).toHaveLength(4)
        expect(venueField.prop('options')).toStrictEqual(expectedOptions)
      })
    })

    describe('when offer is not editable', () => {
      it('should not be possible to modify offer', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = false

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const modifyOfferButton = wrapper.find('#modify-offer-button')
        expect(modifyOfferButton.prop('disabled')).toStrictEqual('disabled')
      })

      it('should display LocalProviderInformation if offer was generated from local provider', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = false
        props.offerer = {
          id: 'AZERT',
        }
        props.product = {
          id: '6GD',
          name: 'super livre',
          thumbUrl: 'http://localhost/image/6GD',
        }
        props.offer = {
          id: 'VAG',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          activeMediation: {
            id: 'MED',
          },
          lastProvider: {
            name: 'TiteLive Stocks',
          },
        }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const localProviderInformationComponent = wrapper.find(LocalProviderInformation)
        expect(localProviderInformationComponent).toHaveLength(1)
        expect(localProviderInformationComponent.prop('offererId')).toBe('AZERT')
        expect(localProviderInformationComponent.prop('isTiteLive')).toBe(true)
        expect(localProviderInformationComponent.prop('isAllocine')).toBe(false)
      })
    })

    describe('when offer is editable', () => {
      beforeEach(() => {
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = true
      })

      it('should be possible to manage stocks', () => {
        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const manageStockButton = wrapper.find('#manage-stocks')
        expect(manageStockButton.prop('disabled')).toStrictEqual('')
      })

      it('should not be possible to modify offer', () => {
        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const modifyOfferButton = wrapper.find('#modify-offer-button')
        expect(modifyOfferButton.prop('disabled')).toStrictEqual('')
      })
    })

    describe('stock management button', () => {
      describe('when offer is from Titelive provider', () => {
        it('should not be possible to change stock values', () => {
          // given
          props.offer.lastProvider = {
            name: 'Titelive',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('disabled')
        })
      })

      describe('when offer is from Allociné provider', () => {
        it('should be possible to change stock values', () => {
          // given
          props.offer.lastProvider = {
            name: 'Allociné',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })

      describe('when offer has been created manually', () => {
        it('should be possible to change stock values', () => {
          // given
          props.offer.lastProvider = null

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })
    })

    describe('event tracking', () => {
      it('should track offer creation', () => {
        // given
        const state = {}

        const action = {
          payload: {
            datum: {
              id: 'Ty5645dgfd',
            },
          },
        }
        jest.spyOn(props.query, 'context').mockReturnValue({
          isCreatedEntity: true,
        })
        const wrapper = shallow(<Offer {...props} />)

        // when
        wrapper.instance().onHandleFormSuccess(state, action)

        // then
        expect(props.trackCreateOffer).toHaveBeenCalledWith('Ty5645dgfd')
      })

      it('should track offer update', () => {
        // given
        const state = {}

        props.offer = {
          id: 'A9',
          lastProvider: null,
        }

        jest.spyOn(props.query, 'context').mockReturnValue({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: false,
        })

        const action = {
          payload: {
            datum: {
              id: 'Ty5645dgfd',
            },
          },
        }
        const wrapper = shallow(<Offer {...props} />)

        // when
        wrapper.instance().onHandleFormSuccess(state, action)

        // then
        expect(props.trackModifyOffer).toHaveBeenCalledWith('A9')
      })
    })
  })
})
