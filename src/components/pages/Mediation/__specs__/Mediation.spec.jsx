import { shallow } from 'enzyme'
import React from 'react'
import Mediation from '../Mediation'

describe('src | components | pages | Mediation', () => {
  let props
  let createOrUpdateMediation
  let getMediation
  let getOffer
  let showOfferModificationErrorNotification
  let showOfferModificationValidationNotification

  beforeEach(() => {
    createOrUpdateMediation = jest.fn()
    getMediation = jest.fn()
    getOffer = jest.fn()
    showOfferModificationErrorNotification = jest.fn()
    showOfferModificationValidationNotification = jest.fn()

    props = {
      createOrUpdateMediation,
      getMediation,
      getOffer,
      history: { push: jest.fn() },
      match: {
        params: {
          offerId: 'AGKA',
        },
      },
      mediation: {},
      offer: {},
      offerer: {},
      showOfferModificationErrorNotification,
      showOfferModificationValidationNotification,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Mediation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render Mediation component with default state', () => {
      // when
      const wrapper = shallow(<Mediation {...props} />)

      // then
      expect(wrapper.state('croppingRect')).toBeNull()
      expect(wrapper.state('inputUrl')).toBe('')
      expect(wrapper.state('imageUrl')).toBeUndefined()
      expect(wrapper.state('image')).toBeNull()
      expect(wrapper.state('isLoading')).toBe(false)
    })

    it('should update imageUrl value from state using thumbPath from mediation when provided', () => {
      // given
      props.mediation = {
        thumbPath: 'thumbPath/',
      }

      // when
      const wrapper = shallow(<Mediation {...props} />)

      // then
      expect(wrapper.state('imageUrl')).toBe('thumbPath/')
    })

    it('should not update imageUrl value from state using thumbPath from mediation when provided', () => {
      // when
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ imageUrl: 'blabla' })

      // then
      expect(wrapper.state('imageUrl')).toBe('blabla')
    })

    it('should update isNew value from state to true when mediationId is "nouveau"', () => {
      // given
      props.match.params = {
        mediationId: 'nouveau',
      }
      // when
      const wrapper = shallow(<Mediation {...props} />)

      // then
      expect(wrapper.state('isNew')).toBe(true)
    })

    it('should not update isNew value from state to true when mediationId is not "nouveau"', () => {
      // given
      props.match.params = {
        mediationId: 'ABCD',
      }
      // when
      const wrapper = shallow(<Mediation {...props} />)

      // then
      expect(wrapper.state('isNew')).toBe(false)
    })
  })

  describe('handleOnChange', () => {
    it('should update credit with input value', () => {
      // given
      const event = {
        target: {
          value: 'myCredit',
        },
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleOnChange(event)

      // then
      expect(wrapper.state('credit')).toBe('myCredit')
    })
  })

  describe('onHandleDataRequest', () => {
    let handleSuccess
    let handleFail

    beforeEach(() => {
      handleSuccess = jest.fn()
      handleFail = jest.fn()
    })

    it('should retrieve mediation when not in creation mode ', () => {
      // given
      props.match.params = {
        mediationId: 'ABCD',
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().onHandleDataRequest(handleSuccess, handleFail)

      // then
      expect(getMediation).toHaveBeenCalledWith('ABCD', expect.any(Function), expect.any(Function))
    })

    it('should not retrieve mediation when in creation mode ', () => {
      // given
      props.match.params = {
        mediationId: 'nouveau',
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().onHandleDataRequest(handleSuccess, handleFail)

      // then
      expect(getMediation).not.toHaveBeenCalled()
    })
  })

  describe('handleFailData', () => {
    let action

    beforeEach(() => {
      action = {
        payload: {
          errors: {
            thumb: [],
          },
        },
      }
    })

    it('should set isLoading in state to false', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      wrapper.instance().handleFailData(wrapper.state(), action)

      // then
      expect(wrapper.state('isLoading')).toBe(false)
    })

    it('should redirect to offer/offerId', () => {
      // given
      props.offer = { id: 'offerId' }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleFailData(wrapper.state(), action)

      // then
      expect(props.history.push).toHaveBeenCalledWith('/offres/offerId')
    })

    it('should show thumb fail notification when error from thumb occurs', () => {
      // given
      action = {
        payload: {
          errors: {
            thumb: ['erreur'],
          },
        },
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleFailData(wrapper.state(), action)

      // then
      expect(showOfferModificationErrorNotification).toHaveBeenCalledWith('erreur')
    })

    it('should show thumbUrl fail notification when error from thumb occurs', () => {
      // given
      action = {
        payload: {
          errors: {
            thumbUrl: ['erreur'],
          },
        },
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleFailData(wrapper.state(), action)

      // then
      expect(showOfferModificationErrorNotification).toHaveBeenCalledWith('erreur')
    })
  })

  describe('handleSuccessData', () => {
    it('should set isLoading in state to false', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      wrapper.instance().handleSuccessData()

      // then
      expect(wrapper.state('isLoading')).toBe(false)
    })

    it('should redirect to offer/offerId', () => {
      // given
      props.offer = { id: 'offerId' }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleSuccessData()

      // then
      expect(props.history.push).toHaveBeenCalledWith('/offres/offerId')
    })
  })

  describe('handleOnOkClick', () => {
    it('should set image and ImageUrl state when url is given in input', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ inputUrl: 'http://input/Url/' })

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.state('image')).toBeNull()
      expect(wrapper.state('imageUrl')).toStrictEqual('http://input/Url/')
    })
  })

  describe('handleOnSubmit', () => {
    it('should set isLoading state to true', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ croppingRect: { x: 1, y: 2 } })

      // when
      wrapper.instance().handleOnSubmit()

      // then
      expect(wrapper.state('isLoading')).toBe(true)
    })

    it('should create or update mediation', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      wrapper.setState({ croppingRect: { x: 1, y: 2 } })

      // when
      wrapper.instance().handleOnSubmit()

      // then
      expect(createOrUpdateMediation).toHaveBeenCalledWith(
        false,
        {},
        expect.any(Object),
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should upload mediation from thumbUrl', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      const state = {
        croppingRect: { x: 1, y: 2 },
        image: 'myImage',
      }
      wrapper.setState(state)
      const expectedBody = new FormData()
      expectedBody.append('offererId', undefined)
      expectedBody.append('offerId', 'AGKA')
      expectedBody.append('credit', undefined)
      expectedBody.append('thumbUrl', 'myImage')
      expectedBody.append('croppingRect[x]', state.croppingRect.x)
      expectedBody.append('croppingRect[y]', state.croppingRect.y)
      expectedBody.append('croppingRect[width]', undefined)
      expectedBody.append('croppingRect[height]', undefined)

      // when
      wrapper.instance().handleOnSubmit()

      // then
      expect(createOrUpdateMediation).toHaveBeenCalledWith(
        false,
        {},
        expectedBody,
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should upload mediation from thumb', () => {
      // given
      const wrapper = shallow(<Mediation {...props} />)
      const state = {
        croppingRect: { x: 1, y: 2 },
        image: { thumb: 'myImage' },
      }
      wrapper.setState(state)
      const expectedBody = new FormData()
      expectedBody.append('offererId', undefined)
      expectedBody.append('offerId', 'AGKA')
      expectedBody.append('credit', undefined)
      expectedBody.append('thumb', { thumb: 'myImage' })
      expectedBody.append('croppingRect[x]', state.croppingRect.x)
      expectedBody.append('croppingRect[y]', state.croppingRect.y)
      expectedBody.append('croppingRect[width]', undefined)
      expectedBody.append('croppingRect[height]', undefined)

      // when
      wrapper.instance().handleOnSubmit()

      // then
      expect(createOrUpdateMediation).toHaveBeenCalledWith(
        false,
        {},
        expectedBody,
        expect.any(Function),
        expect.any(Function)
      )
    })
  })

  describe('handleOnUrlChange', () => {
    it('should set inputUrl in state with value from input', () => {
      // given
      const event = {
        target: {
          value: 'input value',
        },
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleOnUrlChange(event)

      // then
      expect(wrapper.state('inputUrl')).toStrictEqual('input value')
    })
  })

  describe('handleOnUploadClick', () => {
    it('should set state with value from input', () => {
      // given
      const event = {
        target: {
          files: ['my-file'],
        },
      }
      const wrapper = shallow(<Mediation {...props} />)

      // when
      wrapper.instance().handleOnUploadClick(event)

      // then
      expect(wrapper.state('image')).toStrictEqual('my-file')
      expect(wrapper.state('imageUrl')).toBeUndefined()
      expect(wrapper.state('inputUrl')).toStrictEqual('')
    })
  })
})
