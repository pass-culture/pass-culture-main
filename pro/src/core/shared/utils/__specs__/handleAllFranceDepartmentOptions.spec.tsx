import {
  ALL_FRANCE_OPTION_VALUE,
  MAINLAND_OPTION_VALUE,
  allDepartmentValues,
} from '../../interventionOptions'
import { handleAllFranceDepartmentOptions } from '../handleAllFranceDepartmentOptions'

describe('handleAllFranceDepartmentOptions', () => {
  it('should do nothing', () => {
    const currentValues = ['01', '02', '03']
    const previousValues = ['01', '02']
    const mockedSetValue = jest.fn()

    handleAllFranceDepartmentOptions(
      currentValues,
      previousValues,
      mockedSetValue
    )

    expect(mockedSetValue).not.toHaveBeenCalled()
  })

  it('should add "Toute la France" in selected values', () => {
    const currentValues = [...allDepartmentValues, 'culturalPartner']
    const previousValues = [
      ...allDepartmentValues.filter(value => value === '01'),
      'culturalPartner',
    ]
    const mockedSetValue = jest.fn()

    handleAllFranceDepartmentOptions(
      currentValues,
      previousValues,
      mockedSetValue
    )

    expect(mockedSetValue).toHaveBeenCalledWith([
      ...currentValues,
      MAINLAND_OPTION_VALUE,
      ALL_FRANCE_OPTION_VALUE,
    ])
  })

  it('should remove "Toute la France" from selected values', () => {
    const currentValues = [
      ...allDepartmentValues.filter(value => value === '01'),
      ALL_FRANCE_OPTION_VALUE,
      'culturalPartner',
    ]
    const previousValues = [
      ...allDepartmentValues,
      ALL_FRANCE_OPTION_VALUE,
      'culturalPartner',
    ]
    const mockedSetValue = jest.fn()

    handleAllFranceDepartmentOptions(
      currentValues,
      previousValues,
      mockedSetValue
    )

    expect(mockedSetValue).toHaveBeenCalledWith(
      currentValues.filter(value => value !== ALL_FRANCE_OPTION_VALUE)
    )
  })

  it('should select all departments', () => {
    const currentValues = [ALL_FRANCE_OPTION_VALUE, 'culturalPartner', '01']
    const previousValues = ['culturalPartner', '01']
    const mockedSetValue = jest.fn()

    handleAllFranceDepartmentOptions(
      currentValues,
      previousValues,
      mockedSetValue
    )

    expect(mockedSetValue).toHaveBeenCalledWith([
      ALL_FRANCE_OPTION_VALUE,
      'culturalPartner',
      ...allDepartmentValues,
      MAINLAND_OPTION_VALUE,
    ])
  })

  it('should unselect all departments', () => {
    const currentValues = ['culturalPartner', ...allDepartmentValues]
    const previousValues = [
      ALL_FRANCE_OPTION_VALUE,
      'culturalPartner',
      ...allDepartmentValues,
    ]
    const mockedSetValue = jest.fn()

    handleAllFranceDepartmentOptions(
      currentValues,
      previousValues,
      mockedSetValue
    )

    expect(mockedSetValue).toHaveBeenCalledWith(['culturalPartner'])
  })
})
