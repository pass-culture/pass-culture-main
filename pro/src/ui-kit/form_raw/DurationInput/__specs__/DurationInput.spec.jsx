import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import DurationInput from '../DurationInput'

describe('src | components | inputs | DurationInput', () => {
  let props

  beforeEach(() => {
    props = {
      label: 'Durée',
      name: 'duration',
      onChange: jest.fn(),
    }
  })

  it('should display an input with correct name and placeholder', () => {
    // When
    render(<DurationInput {...props} />)

    // Then
    const durationInput = screen.getByRole('textbox')
    expect(durationInput).toBeInTheDocument()
    expect(durationInput).toHaveAttribute('name', props.name)
    expect(durationInput).toHaveProperty('placeholder', 'HH:MM')
  })

  it('should init input with empty text when no initial duration is provided', () => {
    // When
    render(<DurationInput {...props} />)

    // Then
    const durationInput = screen.getByRole('textbox')
    expect(durationInput).toHaveValue('')
  })

  it('should init input with duration in minutes converted in hours and minutes', () => {
    // Given
    props.initialDurationInMinutes = 75

    // When
    render(<DurationInput {...props} />)

    // Then
    const durationInput = screen.getByRole('textbox')
    expect(durationInput).toHaveValue('1:15')
  })

  it('should pad minutes with 0 when initial duration in hours has less than 10 minutes', () => {
    // Given
    props.initialDurationInMinutes = 60

    // When
    render(<DurationInput {...props} />)

    // Then
    const durationInput = screen.getByRole('textbox')
    expect(durationInput).toHaveValue('1:00')
  })

  it('should call onChange prop function with updated duration in minutes when user leave field', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')
    await userEvent.type(durationInput, '1:25')

    // When
    await userEvent.tab()

    // Then
    expect(props.onChange).toHaveBeenCalledWith(85)
    expect(durationInput).toHaveValue('1:25')
  })

  it('should consider as minute a single digit after ":" when user leave field', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')
    await userEvent.type(durationInput, '1:7')

    // When
    await userEvent.tab()

    // Then
    expect(props.onChange).toHaveBeenCalledWith(67)
    expect(durationInput).toHaveValue('1:07')
  })

  it('should consider as hours numbers with no ":" when user leave field', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    await userEvent.type(durationInput, '3')

    // When
    await userEvent.tab()

    // Then
    expect(durationInput).toHaveValue('3:00')

    expect(props.onChange).toHaveBeenCalledWith(180)
  })

  it('should call onChange prop function with null when user remove the duration', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')
    await userEvent.type(durationInput, '1:25')
    await userEvent.tab()
    await userEvent.clear(durationInput)

    // When
    await userEvent.tab()

    // Then
    expect(props.onChange).toHaveBeenLastCalledWith(null)
    expect(durationInput).toHaveValue('')
  })

  it('should accept only numeric caracters', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, 'Accélérer1:13')

    // Then
    expect(durationInput).toHaveValue('1:13')
  })

  it('should accept only one hours-minutes separator', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, '1:34:23')

    // Then
    expect(durationInput).toHaveValue('1:34')
  })

  it('should accept only minutes with two digits', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, '1:346')

    // Then
    expect(durationInput).toHaveValue('1:34')
  })

  it('should not accept minutes to be over 59', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, '1:60')

    // Then
    expect(durationInput).toHaveValue('1:6')
  })

  it('should accept minutes equal to 59', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, '1:59')

    // Then
    expect(durationInput).toHaveValue('1:59')
  })

  it('should not accept minutes without hours', async () => {
    // Given
    render(<DurationInput {...props} />)
    const durationInput = screen.getByRole('textbox')

    // When
    await userEvent.type(durationInput, ':59')

    // Then
    expect(durationInput).toHaveValue('59')
  })
})
