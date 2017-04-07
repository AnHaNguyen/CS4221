'use strict';

/**
 * Construct a new Django formset widget. Directly used by
 * the Jquery plugin.
 * @param {Jquery} selector - A Jquery selector to the formset template, as provided by the Jquery plugin.
 * @param {Object} options - Additional options that override default options. See `$.fn.formset.defaults`.
 * @class
 * @classdesc
 * Django-formset is a simple JQuery plugin that takes care of dynamically
 * managing formsets, and to match input data with the Django POST convention
 * for formsets.
 */

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Formset = function () {
    function Formset(selector, options) {
        _classCallCheck(this, Formset);

        this.selector = selector;
        this.options = options;
        this.flatExtraClasses = options.extraClasses.join(' ');
        if (selector.length) {
            this.initAddButton();
            this.initDeleteButton();
            if (this.options.keepFirst && $('.' + this.options.formCssClass + ':visible').length === 1) {
                this.disableFirstDeleteButton();
            }
        }
    }

    /**
     * Add a new formset to the form. Update the formset field indexes and
     * call a post add handler if present.
     * @access private
     * @param {JQuery} formsetElement - A formset element.
     * @param {Number} formsetCount - The total amount of formsets in the form.
     * @param {Number} addButton - The add button element.
     */


    _createClass(Formset, [{
        key: 'addFormset',
        value: function addFormset(formsetElement, formsetCount, addButton) {
            var _this = this;

            this.applyExtraClasses(formsetElement, formsetCount);
            formsetElement.insertBefore($(addButton)).show();
            formsetElement.find('input,select,textarea,label').each(function (i, el) {
                _this.updateElementIndex($(el), formsetCount);
            });
            $('#id_' + this.options.prefix + '-TOTAL_FORMS').val(formsetCount + 1);
            // If a post-add callback was supplied, call it with the added form:
            if (this.options.added) this.options.added(formsetElement);
        }

        /**
         * Add extra css classes to a formset.
         * @access private
         * @param {JQuery} formsetElement - The formset to apply the classes to.
         * @param {Number} index - The index of the extraClasses array.
         */

    }, {
        key: 'applyExtraClasses',
        value: function applyExtraClasses(formsetElement, index) {
            if (this.options.extraClasses) {
                formsetElement.removeClass(this.flatExtraClasses);
                formsetElement.addClass(this.options.extraClasses[index % this.options.extraClasses.length]);
            }
        }

        /**
         * Create a stripped clone of the last formset and return it.
         * @access private
         * @return {JQuery} - The JQuery selector of the newly cloned formset.
         */

    }, {
        key: 'cloneFormset',
        value: function cloneFormset() {
            var template = $('.' + this.options.formCssClass + ':last').clone(true).removeAttr('id');
            template.find('input:hidden[id $= "-DELETE"]').remove();
            template.find('.' + this.options.errorMessageClass).remove();
            template.find('.' + this.options.formfieldClass).removeClass(this.options.formfieldErrorClass);
            template.find('input,select,textarea,label').each(function (i, el) {
                // If this is a checkbox or radiobutton, uncheck it.
                if ($(el).is('input:checkbox') || $(el).is('input:radio')) {
                    $(el).attr('checked', false);
                } else {
                    $(el).val('');
                }
            });
            return template;
        }

        /**
         * Remove or hide a formset from the form. It's hidden when deleteInput
         * was passed. This way the DELETED value is POST'ed to Django.
         * In case the formset is removed, we also update the TOTAL_FORMS input
         * count.
         * @access private
         * @param {JQuery} [deleteInput] - The related DELETED hidden input.
         * @param {JQuery} [formsetElement] - The formset element about to get deleted.
         */

    }, {
        key: 'deleteFormset',
        value: function deleteFormset(deleteInput, formsetElement) {
            var _this2 = this;

            if (deleteInput.length) {
                // We're dealing with an inline formset; rather than remove
                // this form from the DOM, we'll mark it as deleted and hide
                // it, then let Django handle the deleting.
                deleteInput.val('on');
                formsetElement.hide();
            } else {
                formsetElement.remove();
                var forms = $('.' + this.options.formCssClass);
                // Update the TOTAL_FORMS form count.
                // Also update names and IDs for all remaining form controls so they remain in sequence:
                $('#id_' + this.options.prefix + '-TOTAL_FORMS').val(forms.length);

                var _loop = function _loop(i, formCount) {
                    _this2.applyExtraClasses(forms.eq(i), i);
                    forms.eq(i).find('input,select,textarea,label').each(function (_i, el) {
                        _this2.updateElementIndex($(el), i);
                    });
                };

                for (var i = 0, formCount = forms.length; i < formCount; i++) {
                    _loop(i, formCount);
                }
            }
            // If a post-delete callback was provided, call it with the deleted form:
            if (this.options.deleted) this.options.deleted(formsetElement);
        }

        /**
         * Add a disabled class on the first formset's delete button.
         * @access private
         */

    }, {
        key: 'disableFirstDeleteButton',
        value: function disableFirstDeleteButton() {
            $('.' + this.options.formCssClass + ':visible:first').find('.' + this.options.deleteCssClass).addClass('disabled');
        }

        /**
         * Remove the disabled class from all delete buttons.
         * @access private
         */

    }, {
        key: 'enableDeleteButtons',
        value: function enableDeleteButtons() {
            $('.' + this.options.formCssClass).find('.delete-row').removeClass('disabled');
        }

        /**
         * Check if a formset has fields.
         * @access private
         * @param {JQuery} formsetElement - A formset element.
         * @return {Boolean} - True if the formset has fields.
         */

    }, {
        key: 'hasChildElements',
        value: function hasChildElements(formsetElement) {
            return formsetElement.find('input,select,textarea,label').length > 0;
        }

        /**
         * Add a button and event handler that handles adding a new formset.
         * The add button is added as a table row when the formset is part of a
         * table. Otherwise the button is added as a div element.
         * @access private
         */

    }, {
        key: 'initAddButton',
        value: function initAddButton() {
            var _this3 = this;

            var addButton = void 0;
            // Hide the first formset on init, when there is only one formset and
            // keepFirst is true.
            if (this.options.keepFirst && $('.' + this.options.formCssClass + ':visible').length === 1) {
                this.disableFirstDeleteButton();
            }

            if (this.selector.prop('tagName') === 'TR') {
                // Insert the `add` button in a new table row if forms are laid out as table rows.
                var numCols = this.selector.eq(0).children().length;
                this.selector.parent().append('\n                <tr>\n                    <td class="django-formset-add td" colspan="' + numCols + '">\n                        <a class="' + this.options.addCssClass + '" href="javascript:void(0)">' + this.options.addText + '</a>\n                    </td>\n                </tr>\n            ');
                addButton = this.selector.parent().find('tr:last a');
                addButton.parents('tr').addClass(this.options.formCssClass + '-add');
            } else {
                // Otherwise, insert it immediately after the last form in a div.
                this.selector.filter(':last').after('\n                <div class="django-formset-add div">\n                    <a class="' + this.options.addCssClass + '" href="javascript:void(0)">' + this.options.addText + '</a>\n                </div>\n            ');
                addButton = this.selector.filter(':last').next();
            }

            // Finally add the event handler.
            addButton.click(function (e) {
                var formsetCount = parseInt($('#id_' + _this3.options.prefix + '-TOTAL_FORMS').val(), 10);
                var newFormset = _this3.cloneFormset().clone(true);
                // Why don't we just use `e.currentTarget` here.
                var _addButton = $(e.currentTarget).parents('tr.' + _this3.options.formCssClass + '-add').get(0) || e.currentTarget;
                var forms = $('.' + _this3.options.formCssClass);
                // If a pre-add callback was provided, call it with the row and all forms:
                // To prevent adding return false
                if (_this3.options.beforeAdd) {
                    // Pass a function back to the beforeAdd handler, so the handler
                    // can decide async if/when to add the formset.
                    _this3.options.beforeAdd(newFormset, $('.' + _this3.options.formCssClass + ':visible').length, _addButton, forms, function () {
                        _this3.addFormset(newFormset, formsetCount, _addButton);
                    });
                } else {
                    _this3.addFormset(newFormset, formsetCount, _addButton);
                }

                // Check if the first formset should have a delete button again.
                // Unhide all, because inline styling is copied for new formsets.
                if (_this3.options.keepFirst && $('.' + _this3.options.formCssClass + ':visible').length > 1) {
                    _this3.enableDeleteButtons();
                }
                return false;
            });
        }

        /**
         * Add an eventhandler to the delete button that takes care of
         * deleting the matching formset.
         * @access private
         */

    }, {
        key: 'initDeleteButton',
        value: function initDeleteButton() {
            var _this4 = this;

            this.selector.each(function (i, el) {
                var formsetElement = $(el);
                // Replace default DELETE input checkboxes with hidden inputs.
                _this4.replaceCheckboxes(formsetElement);
                if (_this4.hasChildElements(formsetElement)) {
                    // Add click events to the delete buttons.
                    formsetElement.find('a.' + _this4.options.deleteCssClass).click(function (e) {
                        // The current formset; e.g. the closest formset to the
                        // clicked delete button.
                        var closestFormset = $(e.currentTarget).closest('.' + _this4.options.formCssClass);
                        // POST'ing form-#-DELETE signs Django that the accompanying
                        // object should be marked for deletion.
                        var deleteInput = closestFormset.find('input:hidden[id $= "-DELETE"]');
                        if (_this4.options.beforeDelete) {
                            // Pass a function back to the beforeDelete handler, so
                            // the handler can decide async if/when to add
                            // the formset.
                            _this4.options.beforeDelete(deleteInput, closestFormset, $('.' + _this4.options.formCssClass + ':visible'), function () {
                                _this4.deleteFormset(deleteInput, closestFormset);
                            });
                        } else {
                            _this4.deleteFormset(deleteInput, closestFormset);
                        }
                        if (_this4.options.keepFirst) {
                            if ($('.' + _this4.options.formCssClass + ':visible').length === 1) {
                                _this4.disableFirstDeleteButton();
                            }
                        }
                        return false;
                    });

                    formsetElement.addClass(_this4.options.formCssClass);
                    _this4.applyExtraClasses(formsetElement, i);
                }
            });
        }

        /**
         * Replace DELETE input checkboxes with hidden DELETE input elements.
         * @access private
         * @param {JQuery} formsetElement - The formsetElement to process inputs on.
         */

    }, {
        key: 'replaceCheckboxes',
        value: function replaceCheckboxes(formsetElement) {
            var deleteInput = formsetElement.find('input:checkbox[id $= "-DELETE"]');
            // Replace default formset checkboxes with hidden fields.
            if (deleteInput.length) {
                deleteInput.before('<input type="hidden" name="' + deleteInput.attr('name') + '" id="' + deleteInput.attr('id') + '" />');
                deleteInput.remove();
            }
        }

        /**
         * Name the input fields to the correct formset order.
         * @access private
         * @param {JQuery} elem - A formset field element.
         * @param {Number} index - The formset index to use for the field.
         */

    }, {
        key: 'updateElementIndex',
        value: function updateElementIndex(elem, index) {
            var idRegex = new RegExp('(' + this.options.prefix + '-\\d+-)|(^)');
            var replacement = this.options.prefix + '-' + index + '-';
            if (elem.attr('for')) {
                elem.attr('for', elem.attr('for').replace(idRegex, replacement));
            }
            if (elem.attr('id')) {
                elem.attr('id', elem.attr('id').replace(idRegex, replacement));
            }
            if (elem.attr('name')) {
                elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            }
        }
    }]);

    return Formset;
}();

/**
 * Defines a Jquery plugin. Used as `$(selector).formset(options);`.
 *
 * @param {Object} options - Options that will be passed to the Formset class.
 * @access public
 * @return {Jquery} - The Jquery selector used to init the plugin with.
 */


$.fn.formset = function (options) {
    var selector = $(this);
    new Formset(selector, $.extend({}, $.fn.formset.defaults, options));
    return selector;
};

// Setup plugin defaults.
$.fn.formset.defaults = {
    prefix: 'form', // The form prefix for your django formset
    formsetClone: null, // The jQuery selection cloned to generate new form instances
    addText: '<i class="icon-plus-sign icon-large"></i>',
    deleteText: '<i class="icon-remove-sign icon-large"></i>',
    addCssClass: 'add-row', // CSS class applied to the add link
    deleteCssClass: 'delete-row', // CSS class applied to the delete link
    formCssClass: 'dynamic-form', // CSS class applied to each form in a formset
    extraClasses: [], // Additional CSS classes, which will be applied to each form in turn
    beforeAdd: null, // Function called each time before a new form is added
    beforeDelete: null, // Function called each time before a form is deleted
    added: null, // Function called each time a new form is added
    deleted: null, // Function called each time a form is deleted
    errorMessageClass: 'errorlist', // Error message form element that will be removed when cloning a formset.
    formfieldClass: 'formfield-group', // The formfield container.
    formfieldErrorClass: 'error'
};