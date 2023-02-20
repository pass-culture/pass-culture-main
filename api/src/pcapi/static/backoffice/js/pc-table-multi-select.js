/**
 * @summary Add select all rows features to a table
 * @description Add select all rows feature to a table.
 * You must import this source within your html using a <script> tag to use it,
 * and use a predefined html markup, see example below.
 *
 * @example
 * ```html
 * <div class="my-table-container">
 *   <table>
 *     <tr>
 *       <th><input class="pctms-check-all" type="checkbox" name="pctms-check-all"></th>
 *       <th>Description</th>
 *     </tr>
 *     <tr>
 *       <td>
 *         <input type="checkbox" name="pctms-check-example1">
 *       </td>
 *       <td>
 *         Example 1
 *       </td>
 *       <td>
 *         <input type="checkbox" name="pctms-check-example2">
 *       </td>
 *       <td>
 *         Example 2
 *       </td>
 *     </tr>
 *   </table>
 * </div>
 * <script>
 * const table = new TableMultiSelect(document.querySelector('.my-table-container'))
 * </script>
 * ```
 */
class TableMultiSelect {
    rowsIds = []
    selectedRowsIds = []
    $container = undefined

    constructor($container) {
        this.$container = $container
        this.initialize()
        this.bindEvents()
    }

    get $checkboxes() {
        return this.$container.querySelectorAll("input[name^='pctms-check-']")
    }

    get $batchButtons() {
        return this.$container.querySelectorAll('.pctms-batch-button-group > button')
    }

    get $checkboxAll() {
        return this.$container.querySelector('.pctms-check-all')
    }

    initialize = () => {
        if (this.selectedRowsIds.length === 0) {
            this.disableToolbar(true)
        }
        this.$checkboxes.forEach(($el) => {
            if ($el.id !== this.selectedRowsIds) {
                this.rowsIds.push($el.id)
            }
        })
    }

    bindEvents = () => {
        this.$checkboxes.forEach(($checkbox) => {
            $checkbox.addEventListener("click", (event) => {
                if ($checkbox.checked) {
                    this.disableToolbar(false)
                    if (event.currentTarget.name === this.$checkboxAll.name) {
                        this.selectedRowsIds = []
                        this.selectAll()
                    } else {
                        this.selectedRowsIds.push($checkbox.dataset.id)
                    }
                } else {
                    if (event.currentTarget.name === this.$checkboxAll.name) {
                        this.unselectAll()
                        this.selectedRowsIds = []
                        this.disableToolbar(true)
                    } else {
                        this.popAtIndex(this.selectedRowsIds, $checkbox.dataset.id)
                        if (this.selectedRowsIds.length === 0) {
                            this.disableToolbar(true)
                        }
                    }
                }

                // Manage The indeterminate state of select-all checkbox
                this.$checkboxAll.indeterminate = (this.selectedRowsIds.length < this.rowsIds.length && this.selectedRowsIds.length > 0)
            })
        });
    }

    popAtIndex = (array, element) => {
        const index = array.indexOf(element);
        if (index > -1) {
            array.splice(index, 1)
        }
    }
    selectAll = () => {
        this.$checkboxes.forEach(($checkbox) => {
            $checkbox.checked = true
            if (!this.selectedRowsIds.includes($checkbox.dataset.id)) {
                this.selectedRowsIds.push($checkbox.dataset.id)
            }
        })
    }

    unselectAll = () => {
        this.$checkboxes.forEach(($checkbox) => {
            $checkbox.checked = false
        })
    }

    disableToolbar = (disable) => {
        this.$batchButtons.forEach(($el) => {
            $el.disabled = disable
        })
    }
}
