/**
* @author: Alumuko https://github.com/alumuko/alumuko
* @copyright: Copyright (c) 2021 Alumuko. All rights reserved.
* @license: Licensed under the MIT license. See http://www.opensource.org/licenses/mit-license.php
* @website: https://github.com/alumuko/vanilla-datetimerange-picker
*
* Special thanks to Dan Grossman.
* This program is base on Dan Grossman's bootstrap-daterangepicker (version 3.1)
* I just changed the code a bit to not need jquery.
*/

// IE browser doesn't support "class"
var DateRangePicker;
(function () {
    DateRangePicker = function (element, options, cb) {

        //default settings for options
        this.parentEl = document.body;
        if (typeof element === 'string')
            this.element = document.getElementById(element);
        else
            this.element = element;
        this.startDate = moment().startOf('day');
        this.endDate = moment().endOf('day');
        this.minDate = false;
        this.maxDate = false;
        this.maxSpan = false;
        this.autoApply = false;
        this.singleDatePicker = false;
        this.showDropdowns = false;
        this.minYear = moment().subtract(100, 'year').format('YYYY');
        this.maxYear = moment().add(100, 'year').format('YYYY');
        this.showWeekNumbers = false;
        this.showISOWeekNumbers = false;
        this.showCustomRangeLabel = true;
        this.timePicker = false;
        this.timePicker24Hour = false;
        this.timePickerIncrement = 1;
        this.timePickerSeconds = false;
        this.linkedCalendars = true;
        this.autoUpdateInput = true;
        this.alwaysShowCalendars = false;
        this.ranges = {};

        this.opens = 'right';
        if (this.element.classList.contains('pull-right'))
            this.opens = 'left';

        this.drops = 'down';
        if (this.element.classList.contains('dropup'))
            this.drops = 'up';

        this.buttonClasses = 'btn btn-sm';
        this.applyButtonClasses = 'btn-primary';
        this.cancelButtonClasses = 'btn-default';

        this.locale = {
            direction: 'ltr',
            format: moment.localeData().longDateFormat('L'),
            separator: ' - ',
            applyLabel: 'Apply',
            cancelLabel: 'Cancel',
            weekLabel: 'W',
            customRangeLabel: 'Custom Range',
            daysOfWeek: moment.weekdaysMin(),
            monthNames: moment.monthsShort(),
            firstDay: moment.localeData().firstDayOfWeek()
        };

        this.callback = function() { };

        //some state information
        this.isShowing = false;
        this.leftCalendar = {};
        this.rightCalendar = {};

        //custom options from user
        if (typeof options !== 'object' || options === null)
            options = {};

        //allow setting options with data attributes
        //data-api options will be overwritten with custom javascript options
        options = Object.assign(Object.assign({}, this.element.dataset), options);

        //html template for the picker UI
        if (typeof options.template !== 'string')
            options.template =
            '<div class="daterangepicker">' +
                '<div class="ranges"></div>' +
                '<div class="drp-calendar left">' +
                    '<div class="calendar-table"></div>' +
                    '<div class="calendar-time"></div>' +
                '</div>' +
                '<div class="drp-calendar right">' +
                    '<div class="calendar-table"></div>' +
                    '<div class="calendar-time"></div>' +
                '</div>' +
                '<div class="drp-buttons">' +
                    '<span class="drp-selected"></span>' +
                    '<button class="cancelBtn" type="button"></button>' +
                    '<button class="applyBtn" disabled="disabled" type="button"></button> ' +
                '</div>' +
            '</div>';

        this.parentEl = options.parentEl ? options.parentEl : this.parentEl;
        var templateWrapEl = document.createElement('div');
        templateWrapEl.innerHTML = options.template.trim();
        this.container = templateWrapEl.firstElementChild;
        this.parentEl.insertAdjacentElement('beforeEnd', this.container);

        //
        // handle all the possible options overriding defaults
        //

        if (typeof options.locale === 'object') {

            if (typeof options.locale.direction === 'string')
                this.locale.direction = options.locale.direction;

            if (typeof options.locale.format === 'string')
                this.locale.format = options.locale.format;

            if (typeof options.locale.separator === 'string')
                this.locale.separator = options.locale.separator;

            if (typeof options.locale.daysOfWeek === 'object')
                this.locale.daysOfWeek = options.locale.daysOfWeek.slice();

            if (typeof options.locale.monthNames === 'object')
              this.locale.monthNames = options.locale.monthNames.slice();

            if (typeof options.locale.firstDay === 'number')
              this.locale.firstDay = options.locale.firstDay;

            if (typeof options.locale.applyLabel === 'string')
              this.locale.applyLabel = options.locale.applyLabel;

            if (typeof options.locale.cancelLabel === 'string')
              this.locale.cancelLabel = options.locale.cancelLabel;

            if (typeof options.locale.weekLabel === 'string')
              this.locale.weekLabel = options.locale.weekLabel;

            if (typeof options.locale.customRangeLabel === 'string'){
                //Support unicode chars in the custom range name.
                var elem = document.createElement('textarea');
                elem.innerHTML = options.locale.customRangeLabel;
                var rangeHtml = elem.value;
                this.locale.customRangeLabel = rangeHtml;
            }
        }
        this.container.classList.add(this.locale.direction);

        if (typeof options.startDate === 'string')
            this.startDate = moment(options.startDate, this.locale.format);

        if (typeof options.endDate === 'string')
            this.endDate = moment(options.endDate, this.locale.format);

        if (typeof options.minDate === 'string')
            this.minDate = moment(options.minDate, this.locale.format);

        if (typeof options.maxDate === 'string')
            this.maxDate = moment(options.maxDate, this.locale.format);

        if (typeof options.startDate === 'object')
            this.startDate = moment(options.startDate);

        if (typeof options.endDate === 'object')
            this.endDate = moment(options.endDate);

        if (typeof options.minDate === 'object')
            this.minDate = moment(options.minDate);

        if (typeof options.maxDate === 'object')
            this.maxDate = moment(options.maxDate);

        // sanity check for bad options
        if (this.minDate && this.startDate.isBefore(this.minDate))
            this.startDate = this.minDate.clone();

        // sanity check for bad options
        if (this.maxDate && this.endDate.isAfter(this.maxDate))
            this.endDate = this.maxDate.clone();

        if (typeof options.applyButtonClasses === 'string')
            this.applyButtonClasses = options.applyButtonClasses;

        if (typeof options.applyClass === 'string') //backwards compat
            this.applyButtonClasses = options.applyClass;

        if (typeof options.cancelButtonClasses === 'string')
            this.cancelButtonClasses = options.cancelButtonClasses;

        if (typeof options.cancelClass === 'string') //backwards compat
            this.cancelButtonClasses = options.cancelClass;

        if (typeof options.maxSpan === 'object')
            this.maxSpan = options.maxSpan;

        if (typeof options.dateLimit === 'object') //backwards compat
            this.maxSpan = options.dateLimit;

        if (typeof options.opens === 'string')
            this.opens = options.opens;

        if (typeof options.drops === 'string')
            this.drops = options.drops;

        if (typeof options.showWeekNumbers === 'boolean')
            this.showWeekNumbers = options.showWeekNumbers;

        if (typeof options.showISOWeekNumbers === 'boolean')
            this.showISOWeekNumbers = options.showISOWeekNumbers;

        if (typeof options.buttonClasses === 'string')
            this.buttonClasses = options.buttonClasses;

        if (typeof options.buttonClasses === 'object')
            this.buttonClasses = options.buttonClasses.join(' ');

        if (typeof options.showDropdowns === 'boolean')
            this.showDropdowns = options.showDropdowns;

        if (typeof options.minYear === 'number')
            this.minYear = options.minYear;

        if (typeof options.maxYear === 'number')
            this.maxYear = options.maxYear;

        if (typeof options.showCustomRangeLabel === 'boolean')
            this.showCustomRangeLabel = options.showCustomRangeLabel;

        if (typeof options.singleDatePicker === 'boolean') {
            this.singleDatePicker = options.singleDatePicker;
            if (this.singleDatePicker)
                this.endDate = this.startDate.clone();
        }

        if (typeof options.timePicker === 'boolean')
            this.timePicker = options.timePicker;

        if (typeof options.timePickerSeconds === 'boolean')
            this.timePickerSeconds = options.timePickerSeconds;

        if (typeof options.timePickerIncrement === 'number')
            this.timePickerIncrement = options.timePickerIncrement;

        if (typeof options.timePicker24Hour === 'boolean')
            this.timePicker24Hour = options.timePicker24Hour;

        if (typeof options.autoApply === 'boolean')
            this.autoApply = options.autoApply;

        if (typeof options.autoUpdateInput === 'boolean')
            this.autoUpdateInput = options.autoUpdateInput;

        if (typeof options.linkedCalendars === 'boolean')
            this.linkedCalendars = options.linkedCalendars;

        if (typeof options.isInvalidDate === 'function')
            this.isInvalidDate = options.isInvalidDate;

        if (typeof options.isCustomDate === 'function')
            this.isCustomDate = options.isCustomDate;

        if (typeof options.alwaysShowCalendars === 'boolean')
            this.alwaysShowCalendars = options.alwaysShowCalendars;

        // update day names order to firstDay
        if (this.locale.firstDay != 0) {
            var iterator = this.locale.firstDay;
            while (iterator > 0) {
                this.locale.daysOfWeek.push(this.locale.daysOfWeek.shift());
                iterator--;
            }
        }

        var start, end, range;

        //if no start/end dates set, check if an input element contains initial values
        if (typeof options.startDate === 'undefined' && typeof options.endDate === 'undefined') {
            if(this.element.tagName === 'INPUT' && this.element.type === 'text'){
                var val = this.element.value,
                    split = val.split(this.locale.separator);

                start = end = null;

                if (split.length == 2) {
                    start = moment(split[0], this.locale.format);
                    end = moment(split[1], this.locale.format);
                } else if (this.singleDatePicker && val !== "") {
                    start = moment(val, this.locale.format);
                    end = moment(val, this.locale.format);
                }
                if (start !== null && end !== null) {
                    this.setStartDate(start);
                    this.setEndDate(end);
                }
            }
        }

        if (typeof options.ranges === 'object') {
            let rangesKeys = Object.keys(options.ranges);
            for(let i = 0; i < rangesKeys.length; ++i){
                let range = rangesKeys[i];

                if (typeof options.ranges[range][0] === 'string')
                    start = moment(options.ranges[range][0], this.locale.format);
                else
                    start = moment(options.ranges[range][0]);

                if (typeof options.ranges[range][1] === 'string')
                    end = moment(options.ranges[range][1], this.locale.format);
                else
                    end = moment(options.ranges[range][1]);

                // If the start or end date exceed those allowed by the minDate or maxSpan
                // options, shorten the range to the allowable period.
                if (this.minDate && start.isBefore(this.minDate))
                    start = this.minDate.clone();

                var maxDate = this.maxDate;
                if (this.maxSpan && maxDate && start.clone().add(this.maxSpan).isAfter(maxDate))
                    maxDate = start.clone().add(this.maxSpan);
                if (maxDate && end.isAfter(maxDate))
                    end = maxDate.clone();

                // If the end of the range is before the minimum or the start of the range is
                // after the maximum, don't display this range option at all.
                if ((this.minDate && end.isBefore(this.minDate, this.timepicker ? 'minute' : 'day'))
                  || (maxDate && start.isAfter(maxDate, this.timepicker ? 'minute' : 'day')))
                    continue;

                //Support unicode chars in the range names.
                var elem = document.createElement('textarea');
                elem.innerHTML = range;
                var rangeHtml = elem.value;

                this.ranges[rangeHtml] = [start, end];
            }

            var list = '<ul>';
            for (range in this.ranges) {
                list += '<li data-range-key="' + range + '">' + range + '</li>';
            }
            if (this.showCustomRangeLabel) {
                list += '<li data-range-key="' + this.locale.customRangeLabel + '">' + this.locale.customRangeLabel + '</li>';
            }
            list += '</ul>';
            this.container.querySelector('.ranges').insertAdjacentHTML('afterbegin', list);
        }

        if (typeof cb === 'function') {
            this.callback = cb;
        }

        if (!this.timePicker) {
            this.startDate = this.startDate.startOf('day');
            this.endDate = this.endDate.endOf('day');
            this.container.style.display = 'none';
            this.container.querySelector('.calendar-time').display;
        }

        //can't be used together for now
        if (this.timePicker && this.autoApply)
            this.autoApply = false;

        if (this.autoApply) {
            this.container.classList.add('auto-apply');
        }

        if (typeof options.ranges === 'object')
            this.container.classList.add('show-ranges');

        if (this.singleDatePicker) {
            this.container.classList.add('single');

            this.container.querySelector('.drp-calendar.left').classList.add('single');
            this.container.querySelector('.drp-calendar.left').style.display = 'block';
            this.container.querySelector('.drp-calendar.right').style.display = 'none';
            if (!this.timePicker && this.autoApply) {
                this.container.classList.add('auto-apply');
            }
        }

        if ((typeof options.ranges === 'undefined' && !this.singleDatePicker) || this.alwaysShowCalendars) {
            this.container.classList.add('show-calendar');
        }

        this.container.classList.add('opens' + this.opens);

        //apply CSS classes and labels to buttons
        let applyBtnEl = this.container.querySelector('.applyBtn');
        let cancelBtnEl = this.container.querySelector('.cancelBtn');
        jq.addClass(applyBtnEl, this.buttonClasses);
        jq.addClass(cancelBtnEl, this.buttonClasses);
        if (this.applyButtonClasses.length)
            jq.addClass(applyBtnEl, this.applyButtonClasses);
        if (this.cancelButtonClasses.length)
            jq.addClass(cancelBtnEl, this.cancelButtonClasses);
        jq.html(applyBtnEl, this.locale.applyLabel);
        jq.html(cancelBtnEl, this.locale.cancelLabel);

        //
        // event listeners
        //
        /*
        -- Note: jquery can set event listner before the target element has not been build. Vanilla-JS set event listner LATER.--
        this.container.find('.drp-calendar')
            .on('click.daterangepicker', '.prev', $.proxy(this.clickPrev, this))
            .on('click.daterangepicker', '.next', $.proxy(this.clickNext, this))
            .on('mousedown.daterangepicker', 'td.available', $.proxy(this.clickDate, this))
            .on('mouseenter.daterangepicker', 'td.available', $.proxy(this.hoverDate, this))
            .on('change.daterangepicker', 'select.yearselect', $.proxy(this.monthOrYearChanged, this))
            .on('change.daterangepicker', 'select.monthselect', $.proxy(this.monthOrYearChanged, this))
            .on('change.daterangepicker', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', $.proxy(this.timeChanged, this));
        --------------------------------------------------------------------------------------
        */

        this.clickRangeProxy = function (e) { this.clickRange(e); }.bind(this);
        jq.on(this.container.querySelector('.ranges'), 'click', 'li', this.clickRangeProxy);

        let drpButtonsEl = this.container.querySelector('.drp-buttons');
        this.clickApplyProxy = function (e) { this.clickApply(e); }.bind(this);
        jq.on(drpButtonsEl, 'click', 'button.applyBtn', this.clickApplyProxy);
        this.clickCancelProxy = function (e) { this.clickCancel(e); }.bind(this);
        jq.on(drpButtonsEl, 'click', 'button.cancelBtn', this.clickCancelProxy);

        if (this.element.tagName === 'INPUT' || this.element.tagName === 'BUTTON') {
            this.showProxy = function (e) { this.show(e); }.bind(this);
            jq.on(this.element, 'click', this.showProxy);
            jq.on(this.element, 'focus', this.showProxy);
            this.elementChangedProxy = function (e) { this.elementChanged(e); }.bind(this);
            jq.on(this.element, 'keyup', this.elementChangedProxy);
            this.keydownProxy = function (e) { this.keydown(e); }.bind(this);  //IE 11 compatibility
            jq.on(this.element, 'keydown', this.keydownProxy);
        } else {
            this.toggleProxy = function (e) { this.toggle(e); }.bind(this);
            jq.on(this.element, 'click', this.toggleProxy);
            jq.on(this.element, 'keydown', this.toggleProxy);
        }

        //
        // if attached to a text input, set the initial value
        //

        this.updateElement();

    };

    DateRangePicker.prototype = {

        constructor: DateRangePicker,

        setStartDate: function(startDate) {
            if (typeof startDate === 'string')
                this.startDate = moment(startDate, this.locale.format);

            if (typeof startDate === 'object')
                this.startDate = moment(startDate);

            if (!this.timePicker)
                this.startDate = this.startDate.startOf('day');

            if (this.timePicker && this.timePickerIncrement)
                this.startDate.minute(Math.round(this.startDate.minute() / this.timePickerIncrement) * this.timePickerIncrement);

            if (this.minDate && this.startDate.isBefore(this.minDate)) {
                this.startDate = this.minDate.clone();
                if (this.timePicker && this.timePickerIncrement)
                    this.startDate.minute(Math.round(this.startDate.minute() / this.timePickerIncrement) * this.timePickerIncrement);
            }

            if (this.maxDate && this.startDate.isAfter(this.maxDate)) {
                this.startDate = this.maxDate.clone();
                if (this.timePicker && this.timePickerIncrement)
                    this.startDate.minute(Math.floor(this.startDate.minute() / this.timePickerIncrement) * this.timePickerIncrement);
            }

            if (!this.isShowing)
                this.updateElement();

            this.updateMonthsInView();
        },

        setEndDate: function(endDate) {
            if (typeof endDate === 'string')
                this.endDate = moment(endDate, this.locale.format);

            if (typeof endDate === 'object')
                this.endDate = moment(endDate);

            if (!this.timePicker)
                this.endDate = this.endDate.endOf('day');

            if (this.timePicker && this.timePickerIncrement)
                this.endDate.minute(Math.round(this.endDate.minute() / this.timePickerIncrement) * this.timePickerIncrement);

            if (this.endDate.isBefore(this.startDate))
                this.endDate = this.startDate.clone();

            if (this.maxDate && this.endDate.isAfter(this.maxDate))
                this.endDate = this.maxDate.clone();

            if (this.maxSpan && this.startDate.clone().add(this.maxSpan).isBefore(this.endDate))
                this.endDate = this.startDate.clone().add(this.maxSpan);

            this.previousRightTime = this.endDate.clone();

            jq.html(this.container.querySelector('.drp-selected'), this.startDate.format(this.locale.format) + this.locale.separator + this.endDate.format(this.locale.format));

            if (!this.isShowing)
                this.updateElement();

            this.updateMonthsInView();
        },

        isInvalidDate: function() {
            return false;
        },

        isCustomDate: function() {
            return false;
        },

        updateView: function() {
            if (this.timePicker) {
                this.renderTimePicker('left');
                this.renderTimePicker('right');
                let selectElList = this.container.querySelectorAll('.right .calendar-time select');
                if (!this.endDate) {
                    for (let i = 0; i < selectElList.length; ++i){
                        selectElList[i].disabled = true;
                        selectElList[i].classList.add('disabled');
                    }
                } else {
                    for (let i = 0; i < selectElList.length; ++i){
                        selectElList[i].disabled = false;
                        selectElList[i].classList.remove('disabled');
                    }
                }
            }
            if (this.endDate)
                jq.html(this.container.querySelector('.drp-selected'), this.startDate.format(this.locale.format) + this.locale.separator + this.endDate.format(this.locale.format));
            this.updateMonthsInView();
            this.updateCalendars();
            this.updateFormInputs();
        },

        updateMonthsInView: function() {
            if (this.endDate) {

                //if both dates are visible already, do nothing
                if (!this.singleDatePicker && this.leftCalendar.month && this.rightCalendar.month &&
                    (this.startDate.format('YYYY-MM') == this.leftCalendar.month.format('YYYY-MM') || this.startDate.format('YYYY-MM') == this.rightCalendar.month.format('YYYY-MM'))
                    &&
                    (this.endDate.format('YYYY-MM') == this.leftCalendar.month.format('YYYY-MM') || this.endDate.format('YYYY-MM') == this.rightCalendar.month.format('YYYY-MM'))
                    ) {
                    return;
                }

                this.leftCalendar.month = this.startDate.clone().date(2);
                if (!this.linkedCalendars && (this.endDate.month() != this.startDate.month() || this.endDate.year() != this.startDate.year())) {
                    this.rightCalendar.month = this.endDate.clone().date(2);
                } else {
                    this.rightCalendar.month = this.startDate.clone().date(2).add(1, 'month');
                }

            } else {
                if (this.leftCalendar.month.format('YYYY-MM') != this.startDate.format('YYYY-MM') && this.rightCalendar.month.format('YYYY-MM') != this.startDate.format('YYYY-MM')) {
                    this.leftCalendar.month = this.startDate.clone().date(2);
                    this.rightCalendar.month = this.startDate.clone().date(2).add(1, 'month');
                }
            }
            if (this.maxDate && this.linkedCalendars && !this.singleDatePicker && this.rightCalendar.month > this.maxDate) {
              this.rightCalendar.month = this.maxDate.clone().date(2);
              this.leftCalendar.month = this.maxDate.clone().date(2).subtract(1, 'month');
            }
        },

        updateCalendars: function() {

            if(!this.clickPrevProxy)
                this.clickPrevProxy = function (e) { this.clickPrev(e); }.bind(this);
            if(!this.clickNextProxy)
                this.clickNextProxy = function (e) { this.clickNext(e); }.bind(this);
            if(!this.clickDateProxy)
                this.clickDateProxy = function (e) { this.clickDate(e); }.bind(this);
            if(!this.hoverDateProxy)
                this.hoverDateProxy = function (e) { this.hoverDate(e); }.bind(this);
            if(!this.monthOrYearChangedProxy)
                this.monthOrYearChangedProxy = function (e) { this.monthOrYearChanged(e); }.bind(this);
            if(!this.timeChangedProxy)
                this.timeChangedProxy = function (e) { this.timeChanged(e); }.bind(this);

            /*
            -- Note: by jquery, we can set event listener before the target element has not been build. but we must remove event listener HERE by Vanilla-JS. --
            this.container.find('.drp-calendar')
                .on('click.daterangepicker', '.prev', $.proxy(this.clickPrev, this))
                .on('click.daterangepicker', '.next', $.proxy(this.clickNext, this))
                .on('mousedown.daterangepicker', 'td.available', $.proxy(this.clickDate, this))
                .on('mouseenter.daterangepicker', 'td.available', $.proxy(this.hoverDate, this))
                .on('change.daterangepicker', 'select.yearselect', $.proxy(this.monthOrYearChanged, this))
                .on('change.daterangepicker', 'select.monthselect', $.proxy(this.monthOrYearChanged, this))
                .on('change.daterangepicker', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', $.proxy(this.timeChanged, this));
            --------------------------------------------------------------------------------------
            */
            let drpCalendarElList = this.container.querySelectorAll('.drp-calendar');
            jq.off(drpCalendarElList, 'click', '.prev', this.clickPrevProxy);
            jq.off(drpCalendarElList, 'click', '.next', this.clickNextProxy);
            jq.off(drpCalendarElList, 'mousedown', 'td.available', this.clickDateProxy);
            jq.off(drpCalendarElList, 'mouseenter', 'td.available', this.hoverDateProxy);
            jq.off(drpCalendarElList, 'change', 'select.yearselect', this.monthOrYearChangedProxy);
            jq.off(drpCalendarElList, 'change', 'select.monthselect', this.monthOrYearChangedProxy);
            jq.off(drpCalendarElList, 'change', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', this.timeChangedProxy);
            

            if (this.timePicker) {
                var hour, minute, second;
                if (this.endDate) {
                    hour = parseInt(this.container.querySelector('.left .hourselect').value, 10);
                    minute = parseInt(this.container.querySelector('.left .minuteselect').value, 10);
                    if (isNaN(minute)) {
                        minute = parseInt(jq.findLast(this.container.querySelector('.left .minuteselect')).value, 10);
                    }
                    second = this.timePickerSeconds ? parseInt(this.container.querySelector('.left .secondselect').value, 10) : 0;
                    if (!this.timePicker24Hour) {
                        var ampm = this.container.querySelector('.left .ampmselect').value;
                        if (ampm === 'PM' && hour < 12)
                            hour += 12;
                        if (ampm === 'AM' && hour === 12)
                            hour = 0;
                    }
                } else {
                    hour = parseInt(this.container.querySelector('.right .hourselect').value, 10);
                    minute = parseInt(this.container.querySelector('.right .minuteselect').value, 10);
                    if (isNaN(minute)) {
                        minute = parseInt(jq.findLast(this.container.querySelector('.right .minuteselect')).value, 10);
                    }
                    second = this.timePickerSeconds ? parseInt(this.container.querySelector('.right .secondselect').value, 10) : 0;
                    if (!this.timePicker24Hour) {
                        var ampm = this.container.querySelector('.right .ampmselect').value;
                        if (ampm === 'PM' && hour < 12)
                            hour += 12;
                        if (ampm === 'AM' && hour === 12)
                            hour = 0;
                    }
                }
                this.leftCalendar.month.hour(hour).minute(minute).second(second);
                this.rightCalendar.month.hour(hour).minute(minute).second(second);
            }

            this.renderCalendar('left');
            this.renderCalendar('right');

            //highlight any predefined range matching the current start and end dates
            rangesLiElList = this.container.querySelectorAll('.ranges li');
            for(let i = 0; i < rangesLiElList.length; ++i)
                rangesLiElList[i].classList.remove('active');

            if (this.endDate != null)
                this.calculateChosenLabel();
            
            /*
            -- Note: by jquery, we can set event listener before the target element has not been build. but we must set event listener HERE by Vanilla-JS. --
            this.container.find('.drp-calendar')
                .on('click.daterangepicker', '.prev', $.proxy(this.clickPrev, this))
                .on('click.daterangepicker', '.next', $.proxy(this.clickNext, this))
                .on('mousedown.daterangepicker', 'td.available', $.proxy(this.clickDate, this))
                .on('mouseenter.daterangepicker', 'td.available', $.proxy(this.hoverDate, this))
                .on('change.daterangepicker', 'select.yearselect', $.proxy(this.monthOrYearChanged, this))
                .on('change.daterangepicker', 'select.monthselect', $.proxy(this.monthOrYearChanged, this))
                .on('change.daterangepicker', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', $.proxy(this.timeChanged, this));
            --------------------------------------------------------------------------------------
            */
            jq.on(drpCalendarElList, 'click', '.prev', this.clickPrevProxy);
            jq.on(drpCalendarElList, 'click', '.next', this.clickNextProxy);
            jq.on(drpCalendarElList, 'mousedown', 'td.available', this.clickDateProxy);
            jq.on(drpCalendarElList, 'mouseenter', 'td.available', this.hoverDateProxy);
            jq.on(drpCalendarElList, 'change', 'select.yearselect', this.monthOrYearChangedProxy);
            jq.on(drpCalendarElList, 'change', 'select.monthselect', this.monthOrYearChangedProxy);
            jq.on(drpCalendarElList, 'change', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', this.timeChangedProxy);
    
        },

        renderCalendar: function(side) {

            //
            // Build the matrix of dates that will populate the calendar
            //

            var calendar = side == 'left' ? this.leftCalendar : this.rightCalendar;
            var month = calendar.month.month();
            var year = calendar.month.year();
            var hour = calendar.month.hour();
            var minute = calendar.month.minute();
            var second = calendar.month.second();
            var daysInMonth = moment([year, month]).daysInMonth();
            var firstDay = moment([year, month, 1]);
            var lastDay = moment([year, month, daysInMonth]);
            var lastMonth = moment(firstDay).subtract(1, 'month').month();
            var lastYear = moment(firstDay).subtract(1, 'month').year();
            var daysInLastMonth = moment([lastYear, lastMonth]).daysInMonth();
            var dayOfWeek = firstDay.day();

            //initialize a 6 rows x 7 columns array for the calendar
            var calendar = [];
            calendar.firstDay = firstDay;
            calendar.lastDay = lastDay;

            for (var i = 0; i < 6; i++) {
                calendar[i] = [];
            }

            //populate the calendar with date objects
            var startDay = daysInLastMonth - dayOfWeek + this.locale.firstDay + 1;
            if (startDay > daysInLastMonth)
                startDay -= 7;

            if (dayOfWeek == this.locale.firstDay)
                startDay = daysInLastMonth - 6;

            var curDate = moment([lastYear, lastMonth, startDay, 12, minute, second]);

            var col, row;
            for (var i = 0, col = 0, row = 0; i < 42; i++, col++, curDate = moment(curDate).add(24, 'hour')) {
                if (i > 0 && col % 7 === 0) {
                    col = 0;
                    row++;
                }
                calendar[row][col] = curDate.clone().hour(hour).minute(minute).second(second);
                curDate.hour(12);

                if (this.minDate && calendar[row][col].format('YYYY-MM-DD') == this.minDate.format('YYYY-MM-DD') && calendar[row][col].isBefore(this.minDate) && side == 'left') {
                    calendar[row][col] = this.minDate.clone();
                }

                if (this.maxDate && calendar[row][col].format('YYYY-MM-DD') == this.maxDate.format('YYYY-MM-DD') && calendar[row][col].isAfter(this.maxDate) && side == 'right') {
                    calendar[row][col] = this.maxDate.clone();
                }

            }

            //make the calendar object available to hoverDate/clickDate
            if (side == 'left') {
                this.leftCalendar.calendar = calendar;
            } else {
                this.rightCalendar.calendar = calendar;
            }

            //
            // Display the calendar
            //

            var minDate = side == 'left' ? this.minDate : this.startDate;
            var maxDate = this.maxDate;
            var selected = side == 'left' ? this.startDate : this.endDate;
            var arrow = this.locale.direction == 'ltr' ? {left: 'chevron-left', right: 'chevron-right'} : {left: 'chevron-right', right: 'chevron-left'};

            var html = '<table class="table-condensed">';
            html += '<thead>';
            html += '<tr>';

            // add empty cell for week number
            if (this.showWeekNumbers || this.showISOWeekNumbers)
                html += '<th></th>';

            if ((!minDate || minDate.isBefore(calendar.firstDay)) && (!this.linkedCalendars || side == 'left')) {
                html += '<th class="prev available"><span></span></th>';
            } else {
                html += '<th></th>';
            }

            var dateHtml = this.locale.monthNames[calendar[1][1].month()] + calendar[1][1].format(" YYYY");

            if (this.showDropdowns) {
                var currentMonth = calendar[1][1].month();
                var currentYear = calendar[1][1].year();
                var maxYear = (maxDate && maxDate.year()) || (this.maxYear);
                var minYear = (minDate && minDate.year()) || (this.minYear);
                var inMinYear = currentYear == minYear;
                var inMaxYear = currentYear == maxYear;

                var monthHtml = '<select class="monthselect">';
                for (var m = 0; m < 12; m++) {
                    if ((!inMinYear || (minDate && m >= minDate.month())) && (!inMaxYear || (maxDate && m <= maxDate.month()))) {
                        monthHtml += "<option value='" + m + "'" +
                            (m === currentMonth ? " selected='selected'" : "") +
                            ">" + this.locale.monthNames[m] + "</option>";
                    } else {
                        monthHtml += "<option value='" + m + "'" +
                            (m === currentMonth ? " selected='selected'" : "") +
                            " disabled='disabled'>" + this.locale.monthNames[m] + "</option>";
                    }
                }
                monthHtml += "</select>";

                var yearHtml = '<select class="yearselect">';
                for (var y = minYear; y <= maxYear; y++) {
                    yearHtml += '<option value="' + y + '"' +
                        (y === currentYear ? ' selected="selected"' : '') +
                        '>' + y + '</option>';
                }
                yearHtml += '</select>';

                dateHtml = monthHtml + yearHtml;
            }

            html += '<th colspan="5" class="month">' + dateHtml + '</th>';
            if ((!maxDate || maxDate.isAfter(calendar.lastDay)) && (!this.linkedCalendars || side == 'right' || this.singleDatePicker)) {
                html += '<th class="next available"><span></span></th>';
            } else {
                html += '<th></th>';
            }

            html += '</tr>';
            html += '<tr>';

            // add week number label
            if (this.showWeekNumbers || this.showISOWeekNumbers)
                html += '<th class="week">' + this.locale.weekLabel + '</th>';

            for(let i = 0; i < this.locale.daysOfWeek.length; ++i){
                html += '<th>' + this.locale.daysOfWeek[i] + '</th>';
            }

            html += '</tr>';
            html += '</thead>';
            html += '<tbody>';

            //adjust maxDate to reflect the maxSpan setting in order to
            //grey out end dates beyond the maxSpan
            if (this.endDate == null && this.maxSpan) {
                var maxLimit = this.startDate.clone().add(this.maxSpan).endOf('day');
                if (!maxDate || maxLimit.isBefore(maxDate)) {
                    maxDate = maxLimit;
                }
            }

            for (var row = 0; row < 6; row++) {
                html += '<tr>';

                // add week number
                if (this.showWeekNumbers)
                    html += '<td class="week">' + calendar[row][0].week() + '</td>';
                else if (this.showISOWeekNumbers)
                    html += '<td class="week">' + calendar[row][0].isoWeek() + '</td>';

                for (var col = 0; col < 7; col++) {

                    var classes = [];

                    //highlight today's date
                    if (calendar[row][col].isSame(new Date(), "day"))
                        classes.push('today');

                    //highlight weekends
                    if (calendar[row][col].isoWeekday() > 5)
                        classes.push('weekend');

                    //grey out the dates in other months displayed at beginning and end of this calendar
                    if (calendar[row][col].month() != calendar[1][1].month())
                        classes.push('off', 'ends');

                    //don't allow selection of dates before the minimum date
                    if (this.minDate && calendar[row][col].isBefore(this.minDate, 'day'))
                        classes.push('off', 'disabled');

                    //don't allow selection of dates after the maximum date
                    if (maxDate && calendar[row][col].isAfter(maxDate, 'day'))
                        classes.push('off', 'disabled');

                    //don't allow selection of date if a custom function decides it's invalid
                    if (this.isInvalidDate(calendar[row][col]))
                        classes.push('off', 'disabled');

                    //highlight the currently selected start date
                    if (calendar[row][col].format('YYYY-MM-DD') == this.startDate.format('YYYY-MM-DD'))
                        classes.push('active', 'start-date');

                    //highlight the currently selected end date
                    if (this.endDate != null && calendar[row][col].format('YYYY-MM-DD') == this.endDate.format('YYYY-MM-DD'))
                        classes.push('active', 'end-date');

                    //highlight dates in-between the selected dates
                    if (this.endDate != null && calendar[row][col] > this.startDate && calendar[row][col] < this.endDate)
                        classes.push('in-range');

                    //apply custom classes for this date
                    var isCustom = this.isCustomDate(calendar[row][col]);
                    if (isCustom !== false) {
                        if (typeof isCustom === 'string')
                            classes.push(isCustom);
                        else
                            Array.prototype.push.apply(classes, isCustom);
                    }

                    var cname = '', disabled = false;
                    for (var i = 0; i < classes.length; i++) {
                        cname += classes[i] + ' ';
                        if (classes[i] == 'disabled')
                            disabled = true;
                    }
                    if (!disabled)
                        cname += 'available';

                    html += '<td class="' + cname.replace(/^\s+|\s+$/g, '') + '" data-title="' + 'r' + row + 'c' + col + '">' + calendar[row][col].date() + '</td>';

                }
                html += '</tr>';
            }

            html += '</tbody>';
            html += '</table>';

            jq.html(this.container.querySelector('.drp-calendar.' + side + ' .calendar-table'), html);

        },

        renderTimePicker: function(side) {

            // Don't bother updating the time picker if it's currently disabled
            // because an end date hasn't been clicked yet
            if (side == 'right' && !this.endDate) return;

            var html, selected, minDate, maxDate = this.maxDate;

            if (this.maxSpan && (!this.maxDate || this.startDate.clone().add(this.maxSpan).isBefore(this.maxDate)))
                maxDate = this.startDate.clone().add(this.maxSpan);

            if (side == 'left') {
                selected = this.startDate.clone();
                minDate = this.minDate;
            } else if (side == 'right') {
                selected = this.endDate.clone();
                minDate = this.startDate;

                //Preserve the time already selected
                var timeSelector = this.container.querySelector('.drp-calendar.right .calendar-time');
                if (timeSelector.innerHTML != '') {
                    selected.hour(!isNaN(selected.hour()) ? selected.hour() :  jq.findSelectedOption(timeSelector.querySelector('.hourselect')).value);
                    selected.minute(!isNaN(selected.minute()) ? selected.minute() : jq.findSelectedOption(timeSelector.querySelector('.minuteselect')).value);
                    selected.second(!isNaN(selected.second()) ? selected.second() : jq.findSelectedOption(timeSelector.querySelector('.secondselect')).value);
                    if (!this.timePicker24Hour) {
                        var ampm = jq.findSelectedOption(timeSelector.querySelector('.ampmselect')).value;
                        if (ampm === 'PM' && selected.hour() < 12)
                            selected.hour(selected.hour() + 12);
                        if (ampm === 'AM' && selected.hour() === 12)
                            selected.hour(0);
                    }

                }

                if (selected.isBefore(this.startDate))
                    selected = this.startDate.clone();

                if (maxDate && selected.isAfter(maxDate))
                    selected = maxDate.clone();

            }

            //
            // hours
            //

            html = '<select class="hourselect">';

            var start = this.timePicker24Hour ? 0 : 1;
            var end = this.timePicker24Hour ? 23 : 12;

            for (var i = start; i <= end; i++) {
                var i_in_24 = i;
                if (!this.timePicker24Hour)
                    i_in_24 = selected.hour() >= 12 ? (i == 12 ? 12 : i + 12) : (i == 12 ? 0 : i);

                var time = selected.clone().hour(i_in_24);
                var disabled = false;
                if (minDate && time.minute(59).isBefore(minDate))
                    disabled = true;
                if (maxDate && time.minute(0).isAfter(maxDate))
                    disabled = true;

                if (i_in_24 == selected.hour() && !disabled) {
                    html += '<option value="' + i + '" selected="selected">' + i + '</option>';
                } else if (disabled) {
                    html += '<option value="' + i + '" disabled="disabled" class="disabled">' + i + '</option>';
                } else {
                    html += '<option value="' + i + '">' + i + '</option>';
                }
            }

            html += '</select> ';

            //
            // minutes
            //

            html += ': <select class="minuteselect">';

            for (var i = 0; i < 60; i += this.timePickerIncrement) {
                var padded = i < 10 ? '0' + i : i;
                var time = selected.clone().minute(i);

                var disabled = false;
                if (minDate && time.second(59).isBefore(minDate))
                    disabled = true;
                if (maxDate && time.second(0).isAfter(maxDate))
                    disabled = true;

                if (selected.minute() == i && !disabled) {
                    html += '<option value="' + i + '" selected="selected">' + padded + '</option>';
                } else if (disabled) {
                    html += '<option value="' + i + '" disabled="disabled" class="disabled">' + padded + '</option>';
                } else {
                    html += '<option value="' + i + '">' + padded + '</option>';
                }
            }

            html += '</select> ';

            //
            // seconds
            //

            if (this.timePickerSeconds) {
                html += ': <select class="secondselect">';

                for (var i = 0; i < 60; i++) {
                    var padded = i < 10 ? '0' + i : i;
                    var time = selected.clone().second(i);

                    var disabled = false;
                    if (minDate && time.isBefore(minDate))
                        disabled = true;
                    if (maxDate && time.isAfter(maxDate))
                        disabled = true;

                    if (selected.second() == i && !disabled) {
                        html += '<option value="' + i + '" selected="selected">' + padded + '</option>';
                    } else if (disabled) {
                        html += '<option value="' + i + '" disabled="disabled" class="disabled">' + padded + '</option>';
                    } else {
                        html += '<option value="' + i + '">' + padded + '</option>';
                    }
                }

                html += '</select> ';
            }

            //
            // AM/PM
            //

            if (!this.timePicker24Hour) {
                html += '<select class="ampmselect">';

                var am_html = '';
                var pm_html = '';

                if (minDate && selected.clone().hour(12).minute(0).second(0).isBefore(minDate))
                    am_html = ' disabled="disabled" class="disabled"';

                if (maxDate && selected.clone().hour(0).minute(0).second(0).isAfter(maxDate))
                    pm_html = ' disabled="disabled" class="disabled"';

                if (selected.hour() >= 12) {
                    html += '<option value="AM"' + am_html + '>AM</option><option value="PM" selected="selected"' + pm_html + '>PM</option>';
                } else {
                    html += '<option value="AM" selected="selected"' + am_html + '>AM</option><option value="PM"' + pm_html + '>PM</option>';
                }

                html += '</select>';
            }

            jq.html(this.container.querySelector('.drp-calendar.' + side + ' .calendar-time'), html);

        },

        updateFormInputs: function() {

            if (this.singleDatePicker || (this.endDate && (this.startDate.isBefore(this.endDate) || this.startDate.isSame(this.endDate)))) {
                this.container.querySelector('button.applyBtn').disabled = false;
            } else {
                this.container.querySelector('button.applyBtn').disabled = true;
            }

        },

        move: function() {
            var parentOffset = { top: 0, left: 0 },
                containerTop,
                drops = this.drops;

            var parentRightEdge = window.innerWidth;
            if (!(this.parentEl.tagName === 'BODY')) {
                let parentElOffset = jq.offset(this.parentEl);
                parentOffset = {
                    top: parentElOffset.top - this.parentEl.scrollTop,
                    left: parentElOffset.left - this.parentEl.scrollLeft
                };
                parentRightEdge = this.parentEl.clientWidth + parentElOffset.left;
            }

            /* Note: jquery this.container.outerHeight() returns non 0 even if not showing, but Vanilla-JS this.container.offsetHeight() returns 0 */
            let elementOffset = jq.offset(this.element);
            switch (drops) {
            case 'auto':
                containerTop = elementOffset.top + this.element.offsetHeight - parentOffset.top;
                if (containerTop + this.container.offsetHeight >= this.parentEl.scrollHeight) {
                    containerTop = elementOffset.top - this.container.offsetHeight - parentOffset.top;
                    drops = 'up';
                }
                break;
            case 'up':
                containerTop = elementOffset.top - this.container.offsetHeight - parentOffset.top;
                break;
            default:
                containerTop = elementOffset.top + this.element.offsetHeight - parentOffset.top;
                break;
            }

            // Force the container to it's actual width
            this.container.style.top = '0';
            this.container.style.left = '0';
            this.container.style.right = 'auto';
            var containerWidth = this.container.offsetWidth;

            if (drops == 'up')
                this.container.classList.add('drop-up');
            else
                this.container.classList.remove('drop-up');

            if (this.opens == 'left') {
                var containerRight = parentRightEdge - elementOffset.left - this.element.offsetWidth;
                if (containerWidth + containerRight > window.innerWidth) {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.right = 'auto';
                    this.container.style.left = '9px';
                } else {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.right = containerRight + 'px';
                    this.container.style.left = 'auto';
                }
            } else if (this.opens == 'center') {
                var containerLeft = elementOffset.left - parentOffset.left + this.element.offsetWidth / 2
                    - containerWidth / 2;
                if (containerLeft < 0) {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.right = 'auto';
                    this.container.style.left = '9px';
                } else if (containerLeft + containerWidth > window.innerWidth) {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.left = 'auto';
                    this.container.style.right = '0';
                } else {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.left = containerLeft + 'px';
                    this.container.style.right = 'auto';
                }
            } else {
                var containerLeft = elementOffset.left - parentOffset.left;
                if (containerLeft + containerWidth > window.innerWidth) {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.left = 'auto';
                    this.container.style.right = '0';
                } else {
                    this.container.style.top = containerTop + 'px';
                    this.container.style.left = containerLeft + 'px';
                    this.container.style.right = 'auto';
                }
            }
        },

        show: function(e) {
            if (this.isShowing) return;

            // Create a click proxy that is private to this instance of datepicker, for unbinding
            if(!this._outsideClickProxy)
                this._outsideClickProxy = function (e) { this.outsideClick(e); }.bind(this);

            // Bind global datepicker mousedown for hiding and
            document.addEventListener('mousedown', this._outsideClickProxy);
            // also support mobile devices
            document.addEventListener('touchend', this._outsideClickProxy);
            jq.on(document, 'click', '[data-toggle=dropdown]', this._outsideClickProxy);
            // and also close when focus changes to outside the picker (eg. tabbing between controls)
            document.addEventListener('focusin', this._outsideClickProxy);

            // Reposition the picker if the window is resized while it's open
            if(!this.moveProxy)
                this.moveProxy = function (e) { this.move(e); }.bind(this);
            window.addEventListener('resize', this.moveProxy);

            this.oldStartDate = this.startDate.clone();
            this.oldEndDate = this.endDate.clone();
            this.previousRightTime = this.endDate.clone();

            this.updateView();
            this.container.style.display = 'block';
            this.move();
            this.element.dispatchEvent(new CustomEvent('show.daterangepicker', {bubbles: true, detail: this}));
            this.isShowing = true;
        },

        hide: function(e) {
            if (!this.isShowing) return;

            //incomplete date selection, revert to last values
            if (!this.endDate) {
                this.startDate = this.oldStartDate.clone();
                this.endDate = this.oldEndDate.clone();
            }

            //if a new date range was selected, invoke the user callback function
            if (!this.startDate.isSame(this.oldStartDate) || !this.endDate.isSame(this.oldEndDate))
                this.callback(this.startDate.clone(), this.endDate.clone(), this.chosenLabel);

            //if picker is attached to a text input, update it
            this.updateElement();

            if(this._outsideClickProxy){
                document.removeEventListener('mousedown', this._outsideClickProxy);
                document.removeEventListener('touchend', this._outsideClickProxy);
                jq.off(document, 'click', '[data-toggle=dropdown]', this._outsideClickProxy);
                document.removeEventListener('focusin', this._outsideClickProxy);
            }

            if(this.moveProxy)
                window.removeEventListener('resize', this.moveProxy);

            this.container.style.display = 'none';
            this.element.dispatchEvent(new CustomEvent('hide.daterangepicker', {bubbles: true, detail: this}));
            this.isShowing = false;
        },

        toggle: function(e) {
            if (this.isShowing) {
                this.hide();
            } else {
                this.show();
            }
        },

        outsideClick: function(e) {
            var target = e.target;            
            // if the page is clicked anywhere except within the daterangerpicker/button
            // itself then call this.hide()
            if (
                // ie modal dialog fix
                e.type == "focusin" ||
                target.closest(jq.getSelectorFromElement(this.element)) ||
                target.closest(jq.getSelectorFromElement(this.container)) ||
                target.closest('.calendar-table')
                ) return;
            this.hide();
            this.element.dispatchEvent(new CustomEvent('outsideClick.daterangepicker', {bubbles: true, detail: this}));
        },

        showCalendars: function() {
            this.container.classList.add('show-calendar');
            this.move();
            this.element.dispatchEvent(new CustomEvent('showCalendar.daterangepicker', {bubbles: true, detail: this}));
        },

        hideCalendars: function() {
            this.container.classList.remove('show-calendar');
            this.element.dispatchEvent(new CustomEvent('hideCalendar.daterangepicker', {bubbles: true, detail: this}));
        },

        clickRange: function(e) {

            var label = e.target.dataset.rangeKey;
            this.chosenLabel = label;
            if (label == this.locale.customRangeLabel) {
                this.showCalendars();
            } else {
                var dates = this.ranges[label];
                this.startDate = dates[0];
                this.endDate = dates[1];

                if (!this.timePicker) {
                    this.startDate.startOf('day');
                    this.endDate.endOf('day');
                }

                if (!this.alwaysShowCalendars)
                    this.hideCalendars();
                this.clickApply(e);
            }
        },

        clickPrev: function(e) {
            var cal = e.target.closest('.drp-calendar'); // Note: original use parents not closest.
            if (cal.classList.contains('left')) {
                this.leftCalendar.month.subtract(1, 'month');
                if (this.linkedCalendars)
                    this.rightCalendar.month.subtract(1, 'month');
            } else {
                this.rightCalendar.month.subtract(1, 'month');
            }
            this.updateCalendars();
        },

        clickNext: function(e) {
            var cal = e.target.closest('.drp-calendar'); // Note: original use parents not closest.
            if (cal.classList.contains('left')) {
                this.leftCalendar.month.add(1, 'month');
            } else {
                this.rightCalendar.month.add(1, 'month');
                if (this.linkedCalendars)
                    this.leftCalendar.month.add(1, 'month');
            }
            this.updateCalendars();
        },

        hoverDate: function(e) {

            //ignore dates that can't be selected
            if(!(e.target.classList.contains('available'))) return;

            var title = e.target.dataset.title;
            var row = title.substr(1, 1);
            var col = title.substr(3, 1);
            var cal = e.target.closest('.drp-calendar'); // Note: original use parents not closest.
            var date = cal.classList.contains('left') ? this.leftCalendar.calendar[row][col] : this.rightCalendar.calendar[row][col];

            //highlight the dates between the start date and the date being hovered as a potential end date
            var leftCalendar = this.leftCalendar;
            var rightCalendar = this.rightCalendar;
            var startDate = this.startDate;
            if (!this.endDate) {
                let tdElList = this.container.querySelectorAll('.drp-calendar tbody td');
                for (let i = 0; i < tdElList.length; ++i) {
                    //skip week numbers, only look at dates
                    if(tdElList[i].classList.contains('week')) return;

                    var title = tdElList[i].dataset.title;
                    var row = title.substr(1, 1);
                    var col = title.substr(3, 1);
                    var cal = tdElList[i].closest('.drp-calendar'); // Note: original use parents not closest.
                    var dt = cal.classList.contains('left') ? leftCalendar.calendar[row][col] : rightCalendar.calendar[row][col];
                    if ((dt.isAfter(startDate) && dt.isBefore(date)) || dt.isSame(date, 'day')) {
                        tdElList[i].classList.add('in-range');
                    } else {
                        tdElList[i].classList.remove('in-range');
                    }
                }
            }
        },

        clickDate: function(e) {
        	
            if (!e.target.classList.contains('available')) return;

            var title = e.target.dataset.title;

            var row = title.substr(1, 1);
            var col = title.substr(3, 1);
            var cal = e.target.closest('.drp-calendar');  // Note: original use parents not closest.
            var date = cal.classList.contains('left') ? this.leftCalendar.calendar[row][col] : this.rightCalendar.calendar[row][col];

            //
            // this function needs to do a few things:
            // * alternate between selecting a start and end date for the range,
            // * if the time picker is enabled, apply the hour/minute/second from the select boxes to the clicked date
            // * if autoapply is enabled, and an end date was chosen, apply the selection
            // * if single date picker mode, and time picker isn't enabled, apply the selection immediately
            // * if one of the inputs above the calendars was focused, cancel that manual input
            //

            if (this.endDate || date.isBefore(this.startDate, 'day')) { //picking start
                if (this.timePicker) {
                    var hour = parseInt(this.container.querySelector('.left .hourselect').value, 10);
                    if (!this.timePicker24Hour) {
                        var ampm = this.container.querySelector('.left .ampmselect').value;
                        if (ampm === 'PM' && hour < 12)
                            hour += 12;
                        if (ampm === 'AM' && hour === 12)
                            hour = 0;
                    }
                    var minute = parseInt(this.container.querySelector('.left .minuteselect').value, 10);
                    if (isNaN(minute)) {
                        minute = parseInt(this.container.querySelector('.left .minuteselect option:last').value, 10);
                    }
                    var second = this.timePickerSeconds ? parseInt(this.container.querySelector('.left .secondselect').value, 10) : 0;
                    date = date.clone().hour(hour).minute(minute).second(second);
                }
                this.endDate = null;
                this.setStartDate(date.clone());
            } else if (!this.endDate && date.isBefore(this.startDate)) {
                //special case: clicking the same date for start/end,
                //but the time of the end date is before the start date
                this.setEndDate(this.startDate.clone());
            } else { // picking end
                if (this.timePicker) {
                    var hour = parseInt(this.container.querySelector('.right .hourselect').value, 10);
                    if (!this.timePicker24Hour) {
                        var ampm = this.container.querySelector('.right .ampmselect').value;
                        if (ampm === 'PM' && hour < 12)
                            hour += 12;
                        if (ampm === 'AM' && hour === 12)
                            hour = 0;
                    }
                    var minute = parseInt(this.container.querySelector('.right .minuteselect').value, 10);
                    if (isNaN(minute)) {
                        minute = parseInt(this.container.querySelector('.right .minuteselect option:last').value, 10);
                    }
                    var second = this.timePickerSeconds ? parseInt(this.container.querySelector('.right .secondselect').value, 10) : 0;
                    date = date.clone().hour(hour).minute(minute).second(second);
                }
                this.setEndDate(date.clone());
                if (this.autoApply) {
                  this.calculateChosenLabel();
                  this.clickApply(e);
                }
            }

            if (this.singleDatePicker) {
                this.setEndDate(this.startDate);
                if (!this.timePicker && this.autoApply)
                    this.clickApply(e);
            }

            this.updateView();

            //This is to cancel the blur event handler if the mouse was in one of the inputs
            e.stopPropagation();

        },

        calculateChosenLabel: function () {
            var customRange = true;
            let rangesKey = Object.keys(this.ranges);
            for (let i = 0; i < rangesKey.length; ++i) {
                let range = this.ranges[rangesKey[i]];
                if (this.timePicker) {
                    var format = this.timePickerSeconds ? "YYYY-MM-DD HH:mm:ss" : "YYYY-MM-DD HH:mm";
                    //ignore times when comparing dates if time picker seconds is not enabled
                    if (this.startDate.format(format) == range[0].format(format) && this.endDate.format(format) == range[1].format(format)) {
                        customRange = false;
                        let rangesLiList = this.container.querySelectorAll('.ranges li');
                        rangesLiList[i].classList.add('active');
                        this.chosenLabel = rangesLiList[i].dataset.rangeKey;
                        break;
                    }
                } else {
                    //ignore times when comparing dates if time picker is not enabled
                    if (this.startDate.format('YYYY-MM-DD') == range[0].format('YYYY-MM-DD') && this.endDate.format('YYYY-MM-DD') == range[1].format('YYYY-MM-DD')) {
                        customRange = false;
                        let rangesLiList = this.container.querySelectorAll('.ranges li');
                        rangesLiList[i].classList.add('active');
                        this.chosenLabel = rangesLiList[i].dataset.rangeKey;
                        break;
                    }
                }
            }
            if (customRange) {
                if (this.showCustomRangeLabel) {
                    let rangesLiLastEl = jq.findLast(this.container.querySelectorAll('.ranges li'));
                    if (rangesLiLastEl) {
                        rangesLiLastEl.classList.add('active');
                        this.chosenLabel = rangesLiLastEl.dataset.rangeKey;
                    } else {
                        this.chosenLabel = null;
                    }
                } else {
                    this.chosenLabel = null;
                }
                this.showCalendars();
            }
        },

        clickApply: function(e) {
            this.hide();
            e.target.dispatchEvent(new CustomEvent('apply.daterangepicker', {bubbles: true, detail: this}));
        },

        clickCancel: function(e) {
            this.startDate = this.oldStartDate;
            this.endDate = this.oldEndDate;
            this.hide();
            e.target.dispatchEvent(new CustomEvent('cancel.daterangepicker', {bubbles: true, detail: this}));
        },

        monthOrYearChanged: function(e) {
            var isLeft = e.target.closest('.drp-calendar').classList.contains('left'),
                leftOrRight = isLeft ? 'left' : 'right',
                cal = this.container.querySelector('.drp-calendar.'+leftOrRight);

            // Month must be Number for new moment versions
            var month = parseInt(cal.querySelector('.monthselect').value, 10);
            var year = cal.querySelector('.yearselect').value;

            if (!isLeft) {
                if (year < this.startDate.year() || (year == this.startDate.year() && month < this.startDate.month())) {
                    month = this.startDate.month();
                    year = this.startDate.year();
                }
            }

            if (this.minDate) {
                if (year < this.minDate.year() || (year == this.minDate.year() && month < this.minDate.month())) {
                    month = this.minDate.month();
                    year = this.minDate.year();
                }
            }

            if (this.maxDate) {
                if (year > this.maxDate.year() || (year == this.maxDate.year() && month > this.maxDate.month())) {
                    month = this.maxDate.month();
                    year = this.maxDate.year();
                }
            }

            if (isLeft) {
                this.leftCalendar.month.month(month).year(year);
                if (this.linkedCalendars)
                    this.rightCalendar.month = this.leftCalendar.month.clone().add(1, 'month');
            } else {
                this.rightCalendar.month.month(month).year(year);
                if (this.linkedCalendars)
                    this.leftCalendar.month = this.rightCalendar.month.clone().subtract(1, 'month');
            }
            this.updateCalendars();
        },

        timeChanged: function(e) {
            var cal = e.target.closest('.drp-calendar'),
            isLeft = cal.classList.contains('left');

            var hour = parseInt(cal.querySelector('.hourselect').value, 10);
            var minute = parseInt(cal.querySelector('.minuteselect').value, 10);
            if (isNaN(minute)) {
                minute = parseInt(jq.findLast(cal.querySelectorAll('.minuteselect option')).value, 10);
            }
            var second = this.timePickerSeconds ? parseInt(cal.querySelector('.secondselect').value, 10) : 0;

            if (!this.timePicker24Hour) {
                var ampm = cal.querySelector('.ampmselect').value;
                if (ampm === 'PM' && hour < 12)
                    hour += 12;
                if (ampm === 'AM' && hour === 12)
                    hour = 0;
            }

            if (isLeft) {
                var start = this.startDate.clone();
                start.hour(hour);
                start.minute(minute);
                start.second(second);
                this.setStartDate(start);
                if (this.singleDatePicker) {
                    this.endDate = this.startDate.clone();
                } else if (this.endDate && this.endDate.format('YYYY-MM-DD') == start.format('YYYY-MM-DD') && this.endDate.isBefore(start)) {
                    this.setEndDate(start.clone());
                }
            } else if (this.endDate) {
                var end = this.endDate.clone();
                end.hour(hour);
                end.minute(minute);
                end.second(second);
                this.setEndDate(end);
            }

            //update the calendars so all clickable dates reflect the new time component
            this.updateCalendars();

            //update the form inputs above the calendars with the new time
            this.updateFormInputs();

            //re-render the time pickers because changing one selection can affect what's enabled in another
            let drpCalendarElList = this.container.querySelectorAll('.drp-calendar');
            jq.off(drpCalendarElList, 'change', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', this.timeChangedProxy);

            this.renderTimePicker('left');
            this.renderTimePicker('right');

            jq.on(drpCalendarElList, 'change', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', this.timeChangedProxy);
        },

        elementChanged: function () {
            if(!(this.element.tagName === 'INPUT')) return;
            if(!this.element.value || !this.element.value.length) return;

            var dateString = this.element.value.split(this.locale.separator),
                start = null,
                end = null;

            if (dateString.length === 2) {
                start = moment(dateString[0], this.locale.format);
                end = moment(dateString[1], this.locale.format);
            }

            if (this.singleDatePicker || start === null || end === null) {
                start = moment(this.element.value, this.locale.format);
                end = start;
            }

            if (!start.isValid() || !end.isValid()) return;

            this.setStartDate(start);
            this.setEndDate(end);
            this.updateView();
        },

        keydown: function(e) {
            //hide on tab or enter
            if ((e.keyCode === 9) || (e.keyCode === 13)) {
                this.hide();
            }

            //hide on esc and prevent propagation
            if (e.keyCode === 27) {
                e.preventDefault();
                e.stopPropagation();

                this.hide();
            }
        },

        updateElement: function () {
            if (this.element.tagName === 'INPUT' && this.autoUpdateInput) {
                let newValue = this.startDate.format(this.locale.format);
                if (!this.singleDatePicker) {
                    newValue += this.locale.separator + this.endDate.format(this.locale.format);
                }
                if (newValue !== this.element.value) {
                    this.element.value = newValue;
                    /* this.element.dispatchEvent(new Event('change')); Note: イベント？ */
                }
            }
        },

        remove: function() {

            if (this._outsideClickProxy) {
                // Bind global datepicker mousedown for hiding and
                document.removeEventListener('mousedown', this._outsideClickProxy);
                // also support mobile devices
                document.removeEventListener('touchend', this._outsideClickProxy);
                jq.off(document, 'click', '[data-toggle=dropdown]', this._outsideClickProxy);
                // and also close when focus changes to outside the picker (eg. tabbing between controls)
                document.removeEventListener('focusin', this._outsideClickProxy);
                delete this._outsideClickProxy;
            }
            if(this.moveProxy){
                window.addEventListener('resize', this.moveProxy);
                delete this.moveProxy;
            }
            if(this.clickRangeProxy){
                jq.off(this.container.querySelector('.ranges'), 'click', 'li', this.clickRangeProxy);
                delete this.clickRangeProxy;
            }
            let drpButtonsEl = this.container.querySelector('.drp-buttons');
            if(this.clickApplyProxy){
                jq.off(drpButtonsEl, 'click', 'button.applyBtn', this.clickApplyProxy);
                delete this.clickApplyProxy;
            }
            if(this.clickCancelProxy){
                jq.off(drpButtonsEl, 'click', 'button.cancelBtn', this.clickCancelProxy);
                delete this.clickCancelProxy;
            }
            if (this.element.tagName === 'INPUT' || this.element.tagName === 'BUTTON') {
                if(this.showProxy){
                    jq.off(this.element, 'click', this.showProxy);
                    jq.off(this.element, 'focus', this.showProxy);
                    delete this.showProxy;
                }
                if(this.elementChangedProxy){
                    jq.off(this.element, 'keyup', this.elementChangedProxy);
                    delete this.elementChangedProxy;
                };
                if(this.keydownProxy){
                    jq.off(this.element, 'keydown', this.keydownProxy);
                    delete this.keydownProxy;
                }
            } else {
                if(this.toggleProxy){
                    jq.off(this.element, 'click', this.toggleProxy);
                    jq.off(this.element, 'keydown', this.toggleProxy);
                    delete this.toggleProxy;
                };
            }
            let drpCalendarElList = this.container.querySelectorAll('.drp-calendar');
            if(this.clickPrevProxy){
                jq.off(drpCalendarElList, 'click', '.prev', this.clickPrevProxy);
                delete this.clickPrevProxy;
            }
            if(this.clickNextProxy){
                jq.off(drpCalendarElList, 'click', '.next', this.clickNextProxy);
                delete this.clickNextProxy;
            }
            if(this.clickDateProxy){
                jq.off(drpCalendarElList, 'mousedown', 'td.available', this.clickDateProxy);
                delete this.clickDateProxy;
            }
            if(this.hoverDateProxy){
                jq.off(drpCalendarElList, 'mouseenter', 'td.available', this.hoverDateProxy);
                delete this.hoverDateProxy;
            }
            if(this.monthOrYearChangedProxy){
                jq.off(drpCalendarElList, 'change', 'select.yearselect', this.monthOrYearChangedProxy);
                jq.off(drpCalendarElList, 'change', 'select.monthselect', this.monthOrYearChangedProxy);
                delete this.monthOrYearChangedProxy;
            }
            if(this.timeChangedProxy){
                jq.off(drpCalendarElList, 'change', 'select.hourselect,select.minuteselect,select.secondselect,select.ampmselect', this.timeChangedProxy);
                delete this.timeChangedProxy;
            }
           delete this.container;
           delete this.element.dataset;
        },

        updateRanges: function(newRanges){
            if (typeof newRanges === 'object') {
                jq.off(this.container.querySelector('.ranges'), 'click', 'li', this.clickRangeProxy);
                this.ranges = [];
                let rangesKeys = Object.keys(newRanges);
                for(let i = 0; i < rangesKeys.length; ++i){
                    let range = rangesKeys[i];
    
                    if (typeof newRanges[range][0] === 'string')
                        start = moment(newRanges[range][0], this.locale.format);
                    else
                        start = moment(newRanges[range][0]);
    
                    if (typeof newRanges[range][1] === 'string')
                        end = moment(newRanges[range][1], this.locale.format);
                    else
                        end = moment(newRanges[range][1]);
    
                    // If the start or end date exceed those allowed by the minDate or maxSpan
                    // options, shorten the range to the allowable period.
                    if (this.minDate && start.isBefore(this.minDate))
                        start = this.minDate.clone();
    
                    var maxDate = this.maxDate;
                    if (this.maxSpan && maxDate && start.clone().add(this.maxSpan).isAfter(maxDate))
                        maxDate = start.clone().add(this.maxSpan);
                    if (maxDate && end.isAfter(maxDate))
                        end = maxDate.clone();
    
                    // If the end of the range is before the minimum or the start of the range is
                    // after the maximum, don't display this range option at all.
                    if ((this.minDate && end.isBefore(this.minDate, this.timepicker ? 'minute' : 'day'))
                      || (maxDate && start.isAfter(maxDate, this.timepicker ? 'minute' : 'day')))
                        continue;
    
                    //Support unicode chars in the range names.
                    var elem = document.createElement('textarea');
                    elem.innerHTML = range;
                    var rangeHtml = elem.value;
    
                    this.ranges[rangeHtml] = [start, end];
                }
    
                var list = '<ul>';
                for (range in this.ranges) {
                    list += '<li data-range-key="' + range + '">' + range + '</li>';
                }
                if (this.showCustomRangeLabel) {
                    list += '<li data-range-key="' + this.locale.customRangeLabel + '">' + this.locale.customRangeLabel + '</li>';
                }
                list += '</ul>';
                let rangeNode = this.container.querySelector('.ranges');
                rangeNode.removeChild(rangeNode.firstChild);
                rangeNode.insertAdjacentHTML('afterbegin', list);
            }

            this.clickRangeProxy = function (e) { this.clickRange(e); }.bind(this);
            jq.on(this.container.querySelector('.ranges'), 'click', 'li', this.clickRangeProxy);
        }
        
    };

    // alternate jquery function (subset)
    var jq = {
        addClassSub: function (el, classes) {
            let classsList = classes.split(' ');
            for (let i = 0; i < classsList.length; ++i) {
                el.classList.add(classsList[i].trim());
            }
        },
        addClass: function (el, classes) {
            if (!el)
                return;
            if (typeof el.length === 'number')
                for (let i = 0; i < el.length; ++i)
                    jq.addClassSub(el[i], classes);
            else
                jq.addClassSub(el, classes);
        },
        findLast: function(el) {
            if(!el)
                return null;
            if (typeof el.length === 'number')
                if(el.length > 0)
                    return el[el.length - 1];
                else
                    return null;
            else
                return el;
        },
        findSelectedOption: function(el) {
            if(!el || !el.options || !el.options.length)
                return null;
            for(let i = 0; i < el.options.length; ++i){
                if(el.options[i].selected)
                    return el.options[i];
            }
            return null;
        },
        getSelectorFromElement: function (el) { // no original jquery, tiny implements for closest() function.
            if (!el || !(el instanceof Element))
                return null;
            let selector = el.nodeName.toLowerCase();
            if (el.id)
                return selector + '#' + el.id;
            for (let i = 0; i < el.classList.length; ++i) {
                selector += '.' + el.classList[i];
            }
            return selector;
        },
        html: function (el, html) {
            if (el)
                el.innerHTML = html;
        },
        offset: function (el) {
            if (!el)
                return { top: 0, left: 0 };

            // Return zeros for disconnected and hidden (display: none) elements (gh-2310)
            // Support: IE <=11 only
            // Running getBoundingClientRect on a
            // disconnected node in IE throws an error
            if (!el.getClientRects().length)
                return { top: 0, left: 0 };

            // Get document-relative position by adding viewport scroll to viewport-relative gBCR
            let rect = el.getBoundingClientRect();
            let win = el.ownerDocument.defaultView;
            return {
                top: rect.top + win.pageYOffset,
                left: rect.left + win.pageXOffset
            };
        },
        offSub: function (el, event, listener) {
            if (typeof el.length === 'number')
                for (let i = 0; i < el.length; ++i)
                    el[i].removeEventListener(event, listener);
            else
                el.removeEventListener(event, listener);
        },
        off: function (el, event, param1, param2) {
            if (!el)
                return;
            if (typeof param1 === 'function') { // param is listener
                jq.offSub(el, event, param1);
            } else { // param is selector
                if (typeof el.length === 'number') 
                    for(let i = 0; i < el.length; ++i)
                        jq.offSub(el[i].querySelectorAll(param1), event, param2);
                else
                    jq.offSub(el.querySelectorAll(param1), event, param2);
            }
        },
        onSub: function (el, event, listener) {
            if (typeof el.length === 'number')
                for (let i = 0; i < el.length; ++i)
                    el[i].addEventListener(event, listener);
            else
                el.addEventListener(event, listener);
        },
        on: function (el, event, param1, param2) {
            if (!el)
                return;
            if (typeof param1 === 'function') { // param1 is listener
                jq.onSub(el, event, param1);
            } else { // param1 is selector
                if (typeof el.length === 'number') 
                    for(let i = 0; i < el.length; ++i)
                        jq.onSub(el[i].querySelectorAll(param1), event, param2);
                else
                    jq.onSub(el.querySelectorAll(param1), event, param2);
            }
        },
    };
})();