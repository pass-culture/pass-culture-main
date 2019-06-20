import {mapDispatchToProps} from '../FilterByDateContainer'

describe('src | components | pages | Bookings | FilterByDateContainer', () => {
  describe('mapDispatchToProps', () => {
    it('enable to filter on a specific date', () => {
      // when
      const props = mapDispatchToProps()

      // then
      expect(props).toHaveProperty(
        'selectBookingsForDate'
      )
    })

    it('preserve selected date', () => {
      // given
      const dispatch = jest.fn()
      const props = mapDispatchToProps(dispatch)

      //when
      props.selectBookingsForDate(new Date(2019,6,1))

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: new Date(2019,6,1),
        type: 'BOOKING_SUMMARY_SELECT_DATE',
      })
    })

  })
})
