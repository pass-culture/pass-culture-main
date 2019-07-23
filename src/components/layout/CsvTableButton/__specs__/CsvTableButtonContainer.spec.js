import { mapDispatchToProps } from '../CsvTableButtonContainer'

describe('src | components | layout | CsvTableButton | DisplayButtonContainer', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      href: '/fake-url/fake-uri',
    }

    global.fetch = url => {
      if (url.includes('reimbursements/csv')) {
        return new Response('foo;foo')
      }
      return new Response(400)
    }
  })

  describe('mapDispatchToProps', () => {
    it('should return an object containing two functions', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        downloadFileOrNotifyAnError: expect.any(Function),
        showFailureNotification: expect.any(Function),
      })
    })

    describe('downloadFileOrNotifyAnError', () => {
      it('should return a csv parsed as an object when data fetching succeed', async () => {
        // given
        props.href = 'reimbursements/csv'
        const functions = mapDispatchToProps(dispatch, props)
        const { downloadFileOrNotifyAnError } = functions

        // when
        const result = await downloadFileOrNotifyAnError()

        // then
        expect(result).toStrictEqual({
          data: [],
          headers: ['foo', 'foo'],
        })
      })
    })

    describe('showFailureNotification', () => {
      it('should dispatch an action to trigger notification display', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)
        const { showFailureNotification } = functions

        // when
        showFailureNotification()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            text: "Il n'y a pas de données à afficher.",
            type: 'danger',
          },
          type: 'SHOW_NOTIFICATION',
        })
      })
    })
  })
})
