/**
 * Display a date range picker.
 *
 * We have a minimal set of options, to add more options, you should interface using data attributes
 * To read all options : https://github.com/alumuko/vanilla-datetimerange-picker/
 *
 * Implemented:
 *
 * - `max_date`: if a `datetime.date` is passed, it will disable all date after `maxDate`
 * - `reset_to_blank`: if `true`, cancel button will have text "Réinitialiser" and set value to empty string
 * - `calendar_start_date`: if a `datetime.date` is passed, it will set calendar start date when opening calendar
 * - `calendar_end_date`: if a `datetime.date` is passed, it will set calendar end date when opening calendar
 *
 * @example
 * from_to_date = fields.PCDateRangeField(
 *     "Créées entre",
 *     validators=(wtforms.validators.Optional(),),
 *     max_date=datetime.date.today(),
 *     reset_to_blank=False,
 *     calendar_start_date=datetime.date.today() - timedelta(days=60),
 *     calendar_end_date=datetime.date.today() - timedelta(days=30),
 * )
 */
class PcDateRangeField extends PcAddOn {

    static DATE_RANGE_SELECTOR = '.pc-date-range-field'
    static DATE_FORMAT = 'DD/MM/YYYY'
    static LOCALE_DAY_OF_THE_WEEK =  ['Di', 'Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa']
    static LOCALE_MONTH_NAMES = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout', 'Sep', 'Oct', 'Nov', 'Déc']
    static LOCALE_FIRST_DAY = 1
    static LOCALE_APPLY_LABEL = 'Appliquer'
    static LOCALE_CANCEL_LABEL = 'Annuler'
    static LOCALE_SEPARATOR = ' - '

    state = []

    get $$dateRange() {
        return document.querySelectorAll(PcDateRangeField.DATE_RANGE_SELECTOR)
    }


    get locale() {
        return {
            format: PcDateRangeField.DATE_FORMAT,
            daysOfWeek: PcDateRangeField.LOCALE_DAY_OF_THE_WEEK,
            monthNames: PcDateRangeField.LOCALE_MONTH_NAMES,
            firstDay: PcDateRangeField.LOCALE_FIRST_DAY,
            applyLabel: PcDateRangeField.LOCALE_APPLY_LABEL,
            cancelLabel: PcDateRangeField.LOCALE_CANCEL_LABEL,
            separator: PcDateRangeField.LOCALE_SEPARATOR,
        }
    }

    bindEvents = () => {
        const options = {
            autoUpdateInput: false,
            locale: this.locale,
            maxDate: new Date(),
            autoApply: false,
            alwaysShowCalendars: true,
            linkedCalendars: false,
        }

        this.$$dateRange.forEach(($dateRange) => {
            const {
                maxDate,
                resetToBlank,
                calendarStartDate,
                calendarEndDate,
            } = $dateRange.dataset
            const dateRangePicker = new DateRangePicker($dateRange, {
                ...options,
                maxDate: maxDate ? moment(maxDate, PcDateRangeField.DATE_FORMAT) : undefined,
                locale: {
                    ...options.locale,
                    cancelLabel: resetToBlank ? 'Réinitialiser' : PcDateRangeField.LOCALE_CANCEL_LABEL,
                }
            })
            if (calendarStartDate) {
                dateRangePicker.setStartDate(moment(calendarStartDate, PcDateRangeField.DATE_FORMAT))
            }
            if (calendarEndDate) {
                dateRangePicker.setEndDate(moment(calendarEndDate, PcDateRangeField.DATE_FORMAT))
            }
            this.state.push(dateRangePicker)
        })

        addEventListener('apply.daterangepicker', this.#applyDaterangePicker)
        addEventListener('cancel.daterangepicker', this.#cancelDaterangePicker)
    }

    unbindEvents = () => {
        this.state.forEach(($dateRange) => {
            $dateRange.remove()
        })
        this.state = []

        removeEventListener('apply.daterangepicker', this.#applyDaterangePicker)
        removeEventListener('cancel.daterangepicker', this.#cancelDaterangePicker)
    }

    #applyDaterangePicker(event) {
        const detail = event.detail
        detail.element.value =
            `${detail.startDate.format(PcDateRangeField.DATE_FORMAT)}${PcDateRangeField.LOCALE_SEPARATOR}${detail.endDate.format(PcDateRangeField.DATE_FORMAT)}`
    }

    #cancelDaterangePicker(event) {
      if (event.detail.element.dataset.resetToBlank) {
        event.detail.element.value = ''
        return
      }
      this.state.forEach((dateRangePicker) => {
        const {
            calendarStartDate,
            calendarEndDate,
        } = $dateRange.dataset
        if (calendarStartDate) {
            dateRangePicker.setStartDate(moment(calendarStartDate, PcDateRangeField.DATE_FORMAT))
        }
        if (calendarEndDate) {
            dateRangePicker.setEndDate(moment(calendarEndDate, PcDateRangeField.DATE_FORMAT))
        }
    })
    }
}
