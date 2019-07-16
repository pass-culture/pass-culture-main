import { shallow } from 'enzyme'
import SelectSourceField from '../SelectSourceField'

describe('src | components | pages | Venue | VenueProvidersManager | form | SelectSourceField', () => {
  let props
  let handleChange

  beforeEach(() => {
    handleChange = jest.fn()
    props = {
      handleChange,
      providers: [
        { id: 'A', name: 'A', requireProviderIdentifier: false },
        { id: 'B', name: 'B', requireProviderIdentifier: true },
      ],
      venueProviders: [{ id: 'C', providerId: 'A' }, { id: 'B', providerId: 'B' }],
    }
  })

  it('should render a select component with three options with right props, including one disabled option', () => {
    // when
    const selectRendered = shallow(SelectSourceField({ ...props })({}))

    // then
    const options = selectRendered.find('option')
    expect(options).toHaveLength(3)
    expect(selectRendered.prop('className')).toBe('field-select')
    expect(selectRendered.prop('id')).toBe('provider-options')
    expect(options.at(0).prop('value')).toStrictEqual(
      '{"id":"default","name":"Choix de la source"}'
    )
    expect(options.at(1).prop('value')).toStrictEqual(
      '{"id":"A","name":"A","requireProviderIdentifier":false}'
    )
    expect(options.at(1).prop('disabled')).toBe(true)
    expect(options.at(2).prop('value')).toStrictEqual(
      '{"id":"B","name":"B","requireProviderIdentifier":true}'
    )
    expect(options.at(2).prop('disabled')).toStrictEqual(false)
  })
})
