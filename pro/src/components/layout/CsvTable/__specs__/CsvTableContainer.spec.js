import { mapDispatchToProps } from '../CsvTableContainer'

describe('src | components | layout | CsvTable | CsvTableContainer', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      location: {
        state: '/path-to-csv',
      },
    }

    global.fetch = url => {
      if (url.includes('reimbursements/csv')) {
        return new Response('foo;foo')
      }
      throw new Error()
    }
  })

  describe('mapDispatchToProps', () => {
    it('should return an object containing two functions', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        downloadFileOrNotifyAnError: expect.any(Function),
      })
    })

    describe('downloadFileOrNotifyAnError', () => {
      it('should return a csv parsed as an object when data fetching succeed', async () => {
        // given
        props.location.state = 'reimbursements/csv'
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

      it('should throw an Error when data retrieval failed', async () => {
        // given
        props.location.state = '/fake-path'
        const functions = mapDispatchToProps(dispatch, props)
        const { downloadFileOrNotifyAnError } = functions

        // when
        await expect(downloadFileOrNotifyAnError()).rejects.toThrow(
          'Erreur lors du téléchargement des données.'
        )
      })
    })
  })
})
