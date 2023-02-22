/**
 * Add select all rows features to a table
 *
 * @example
 * <table data-table-multi-select-id="my-unique-id">
 *   <tr>
 *     <th><input type="checkbox" name="pc-table-multiselect-check-all"></th>
 *     <th>Description</th>
 *   </tr>
 *   <tr>
 *     <td><input type="checkbox" name="pc-table-multi-check-example1"></td>
 *     <td>Example 1</td>
 *     <td><input type="checkbox" name="pc-table-multi-check-example2"></td>
 *     <td>Example 2</td>
 *   </tr>
 * </table>
 */
class PcTableMultiSelect extends PcAddOn {

  static TABLES_SELECTOR = 'table[data-table-multi-select-id]'
  static CHECKBOXES_SELECTOR = "input[name^='pc-table-multi-select-check-']"
  static BATCH_BUTTONS_SELECTOR = '.pc-table-multi-select-batch-button-group > button'
  static CHECKBOX_ALL_SELECTOR = 'input[name="pc-table-multi-select-check-all"]'

  state = {}

  get $tables() {
    return document.querySelectorAll(PcTableMultiSelect.TABLES_SELECTOR)
  }

  initialize = () => {
    this.$tables.forEach(($table) => {
      const { tableMultiSelectId } = $table.dataset
      $table.querySelectorAll(PcTableMultiSelect.CHECKBOXES_SELECTOR).forEach(($checkbox) => {
        $checkbox.dataset.tableMultiSelectId = tableMultiSelectId
      })
      if (!this.state[tableMultiSelectId]) {
        this.state[tableMultiSelectId] = {
          rowsIds: [],
          selectedRowsIds: [],
        }
      }
      if (this.state[tableMultiSelectId].selectedRowsIds.length === 0) {
        this.#disableToolbar($table, true)
      }
    })
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcTableMultiSelect.CHECKBOXES_SELECTOR, this.#onCheckboxClick)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcTableMultiSelect.CHECKBOXES_SELECTOR, this.#onCheckboxClick)
  }

  #getBatchButtons($table) {
    return $table.parentElement.querySelectorAll(PcTableMultiSelect.BATCH_BUTTONS_SELECTOR)
  }

  #getCheckboxAll($table) {
    return $table.querySelector(PcTableMultiSelect.CHECKBOX_ALL_SELECTOR)
  }

  #getCheckboxes($table) {
    return $table.querySelectorAll(PcTableMultiSelect.CHECKBOXES_SELECTOR)
  }

  #onCheckboxClick = (event) => {
    const { id, tableMultiSelectId } = event.target.dataset
    const $table = document.querySelector(`${PcTableMultiSelect.TABLES_SELECTOR.slice(0, -1)}="${tableMultiSelectId}"]`)

    if (event.target.checked) {
      this.#disableToolbar($table, false)
      if (event.target.name === this.#getCheckboxAll($table).name) {
        this.state[tableMultiSelectId].selectedRowsIds = []
        this.#selectAll($table)
      } else {
        this.state[tableMultiSelectId].selectedRowsIds.push(id)
      }
    } else {
      if (event.target.name === this.#getCheckboxAll($table).name) {
        this.#unselectAll($table)
        this.state[tableMultiSelectId].selectedRowsIds = []
        this.#disableToolbar($table, true)
      } else {
        PcUtils.popAtIndex(this.state[tableMultiSelectId].selectedRowsIds, id)
        if (this.state[tableMultiSelectId].selectedRowsIds.length === 0) {
          this.#disableToolbar($table, true)
        }
      }
    }

    // Manage The indeterminate state of select-all checkbox
    this.#getCheckboxAll($table).indeterminate = (this.state[tableMultiSelectId].selectedRowsIds.length < this.state[tableMultiSelectId].rowsIds.length && this.state[tableMultiSelectId].selectedRowsIds.length > 0)
  }

  #selectAll = ($table) => {
    const { tableMultiSelectId } = $table.dataset
    this.#getCheckboxes($table).forEach(($checkbox) => {
      $checkbox.checked = true
      if (!this.state[tableMultiSelectId].selectedRowsIds.includes($checkbox.dataset.id)) {
        this.state[tableMultiSelectId].selectedRowsIds.push($checkbox.dataset.id)
      }
    })
  }

  #unselectAll = ($table) => {
    this.#getCheckboxes($table).forEach(($checkbox) => {
      $checkbox.checked = false
    })
  }

  #disableToolbar = ($table, disable) => {
    this.#getBatchButtons($table).forEach(($button) => {
      $button.disabled = disable
    })
    this.#getCheckboxes($table).forEach(($checkbox) => {
      const { tableMultiSelectId } = $table.dataset
      if ($checkbox.id !== this.state[tableMultiSelectId].selectedRowsIds) {
        this.state[tableMultiSelectId].rowsIds.push($checkbox.id)
      }
    })
  }
}
