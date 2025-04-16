/**
 * Adds select all rows features to a table.
 *
 * When rows selection change, it emit a `CustomEvent` named `pcTableMultiSelect:change` with:
 *
 * - `detail.tableMultiSelectId`: the unique identifier of the table multi select,
 * - `detail.rowsIds`: the list of table entities identifier,
 * - `detail.selectedRowsIds`: the list of selected identifier.
 *
 * @example
 * // create a new table multi select using HTML markup
 * <table data-table-multi-select-id="my-unique-id">
 *   <tr>
 *     <th><input type="checkbox" name="pc-table-multi-select-check-all"></th>
 *     <th>Description</th>
 *   </tr>
 *   <tr>
 *     <td><input type="checkbox" name="pc-table-multi-select-check-example1"></td>
 *     <td>Example 1</td>
 *     <td><input type="checkbox" name="pc-table-multi-select-check-example2"></td>
 *     <td>Example 2</td>
 *   </tr>
 * </table>
 *
 * @example
 * // Example of addon which listen for selection change of any pc table multi select
 * class PcExample extends PcAddOn {
 *   bindEvents() {
 *     addEventListener('pcTableMultiSelect:change', this.#onUpdate)
 *   }
 *
 *   unbindEvents() {
 *     removeEventListener('pcTableMultiSelect:change', this.#onUpdate)
 *   }
 *
 *   #onUpdate(event) {
 *     console.log(event.detail)
 *   }
 * }
 */
class PcTableMultiSelect extends PcAddOn {
  /** Unique identifier of this addon, in order to reference it from another add on */
  static ID = 'PcTableMultiSelectId'
  static TABLES_SELECTOR = 'table[data-table-multi-select-id]'
  static CHECKBOXES_SELECTOR = "input[name^='pc-table-multi-select-check-']:not([name='pc-table-multi-select-check-all'])"
  static CHECKBOX_ALL_SELECTOR = 'input[name="pc-table-multi-select-check-all"]'

  state = {}

  get $tables() {
    return document.querySelectorAll(PcTableMultiSelect.TABLES_SELECTOR)
  }

  initialize = () => {
    this.refreshState()
  }

  refreshState = () => {
    this.$tables.forEach(($table) => {
      const rowsIds = new Set([])
      const { tableMultiSelectId } = $table.dataset
      if(!$table.querySelector(PcTableMultiSelect.CHECKBOX_ALL_SELECTOR)){
        return
      }
      $table.querySelector(PcTableMultiSelect.CHECKBOX_ALL_SELECTOR).dataset.tableMultiSelectId = tableMultiSelectId
      $table.querySelectorAll(PcTableMultiSelect.CHECKBOXES_SELECTOR).forEach(($checkbox) => {
        $checkbox.dataset.tableMultiSelectId = tableMultiSelectId
        rowsIds.add($checkbox.dataset.id)
      })
      this.state[tableMultiSelectId] = {
        rowsIds,
        selectedRowsIds: new Set(this.state[tableMultiSelectId] ? this.state[tableMultiSelectId].selectedRowsIds || [] : []),
      }
    })
  }
  bindEvents = () => {
    this.refreshState()
    EventHandler.on(document.body, 'click', PcTableMultiSelect.CHECKBOXES_SELECTOR, this.#onCheckboxClick)
    EventHandler.on(document.body, 'click', PcTableMultiSelect.CHECKBOX_ALL_SELECTOR, this.#onCheckboxAllClick)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcTableMultiSelect.CHECKBOXES_SELECTOR, this.#onCheckboxClick)
    EventHandler.off(document.body, 'click', PcTableMultiSelect.CHECKBOX_ALL_SELECTOR, this.#onCheckboxAllClick)
  }

  #getTableFromTableMultiSelectId(tableMultiSelectId) {
    return document.querySelector(`${PcTableMultiSelect.TABLES_SELECTOR.slice(0, -1)}="${tableMultiSelectId}"]`)
  }

  #getCheckboxAll($table) {
    return $table.querySelector(PcTableMultiSelect.CHECKBOX_ALL_SELECTOR)
  }

  #getCheckboxes($table) {
    return $table.querySelectorAll(PcTableMultiSelect.CHECKBOXES_SELECTOR)
  }

  #onCheckboxAllClick = (event) => {
    const { tableMultiSelectId } = event.target.dataset
    const $table = this.#getTableFromTableMultiSelectId(tableMultiSelectId)
    this.#batchSelect($table, event.target.checked)
  }

  #onCheckboxClick = (event) => {
    const { id, tableMultiSelectId } = event.target.dataset
    const $table = this.#getTableFromTableMultiSelectId(tableMultiSelectId)

    if (event.target.checked) {
      this.state[tableMultiSelectId].selectedRowsIds.add(id)
    } else {
      this.state[tableMultiSelectId].selectedRowsIds.delete(id)
    }

    // Manage The indeterminate state of select-all checkbox
    this.#getCheckboxAll($table).indeterminate = (this.state[tableMultiSelectId].selectedRowsIds.size < this.state[tableMultiSelectId].rowsIds.size && this.state[tableMultiSelectId].selectedRowsIds.size > 0)

    this.#emitChangeEvent($table)
  }

  #batchSelect = ($table, checked) => {
    const { tableMultiSelectId } = $table.dataset
    const selectedRowsIds = new Set([])
    this.#getCheckboxes($table).forEach(($checkbox) => {
      $checkbox.checked = checked
      if (checked) {
        selectedRowsIds.add($checkbox.dataset.id)
      }
    })
    this.state[tableMultiSelectId].selectedRowsIds = selectedRowsIds
    this.#emitChangeEvent($table)
  }

  #emitChangeEvent = ($table) => {
    const { tableMultiSelectId } = $table.dataset
    dispatchEvent(new CustomEvent(`${this.name}:change`, {
      detail: {
        tableMultiSelectId,
        ...this.state[tableMultiSelectId],
      }
    }))
  }
}
