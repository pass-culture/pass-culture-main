import Box from '@mui/material/Box'
import TextField from '@mui/material/TextField'
import { frFR, LocalizationProvider } from '@mui/x-date-pickers-pro'
import { AdapterDateFns } from '@mui/x-date-pickers-pro/AdapterDateFns'
import {
  DateRangePicker,
  DateRange,
} from '@mui/x-date-pickers-pro/DateRangePicker'
import { add } from 'date-fns'
import frLocale from 'date-fns/locale/fr'
import * as React from 'react'

function getWeeksAfter(date: Date | null, amount: number) {
  return date ? add(date, { weeks: amount }) : undefined
}
type Props = {
  value: DateRange<Date>
  setNewValue: (value: DateRange<Date>) => void
}
export default function MinMaxDateRangePicker({ value, setNewValue }: Props) {
  return (
    <LocalizationProvider
      dateAdapter={AdapterDateFns}
      adapterLocale={frLocale}
      localeText={
        frFR.components.MuiLocalizationProvider.defaultProps.localeText
      }
    >
      <DateRangePicker
        value={value}
        maxDate={getWeeksAfter(value[0], 4)}
        inputFormat={'dd/MM/yyyy'}
        onChange={newValue => {
          setNewValue(newValue)
        }}
        renderInput={(startProps, endProps) => (
          <React.Fragment>
            <TextField {...startProps} label={'Date de début'} />
            <Box sx={{ mx: 2 }}> à </Box>
            <TextField {...endProps} label={'Date de fin'} />
          </React.Fragment>
        )}
      />
    </LocalizationProvider>
  )
}
