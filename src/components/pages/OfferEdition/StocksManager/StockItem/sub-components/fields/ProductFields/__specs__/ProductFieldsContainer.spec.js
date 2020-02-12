import { mapDispatchToProps } from '../ProductFieldsContainer'

describe('components | OfferEdition | ProductFieldsContainer', () => {
  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('assignModalConfig', () => {
      it('should dispatch assign modal config action', () => {
        // given
        const functions = mapDispatchToProps(dispatch)
        const { assignModalConfig } = functions

        // when
        assignModalConfig('fake className')

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            extraClassName: 'fake className',
          },
          type: 'ASSIGN_MODAL_CONFIG',
        })
      })
    })
  })
})
