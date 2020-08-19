import User from '../../profile/ValueObjects/User'
import { mapDispatchToProps, mapStateToProps, mergeProps } from '../HomeContainer'
import { updateCurrentUser } from '../../../../redux/actions/currentUser'

jest.mock('../../../../redux/actions/currentUser', () => ({
  updateCurrentUser: jest.fn(),
}))

describe('home container', () => {
  describe('map state to props', () => {
    it('should contain geocolation and user', () => {
      // Given
      const state = {
        currentUser: new User(),
        geolocation: { latitude: 5.98374, longitude: 5.23984 },
      }

      // When
      const props = mapStateToProps(state)

      // Then
      expect(props.user).toStrictEqual(state.currentUser)
      expect(props.geolocation).toStrictEqual(state.geolocation)
    })
  })

  describe('map dispatch to props', () => {
    it('should contain updateCurrentUser', () => {
      // When
      const props = mapDispatchToProps()

      // Then
      expect(props.updateCurrentUser).toStrictEqual(updateCurrentUser)
    })
  })

  describe('merge props', () => {
    it('should contain a function to track user who have seen all modules', () => {
      // Given
      const ownProps = { tracking: { trackEvent: jest.fn() } }
      const props = mergeProps({}, {}, ownProps)

      // When
      props.trackAllModulesSeen(5)

      // Then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'AllModulesSeen',
        name: 'Number of modules: 5',
      })
    })

    it('should contain a function to track user who have seen all tiles', () => {
      // Given
      const ownProps = { tracking: { trackEvent: jest.fn() } }
      const props = mergeProps({}, {}, ownProps)

      // When
      props.trackAllTilesSeen('Exclu', 3)

      // Then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'AllTilesSeen',
        name: 'Module name: Exclu - Number of tiles: 3',
      })
    })
  })
})
