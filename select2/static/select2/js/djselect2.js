(function ( $ ) {

    var pluginName = 'djselect2';
    var defaults = {};

    // The actual plugin constructor
    function Plugin( element, options ) {
        this.element = $(element);
        this.defaults = defaults;
        this.name = pluginName;

        // Store this plugin on the element for later retrieval
        this.element.data('djselect2', this);

        // Retrieve information from the element.
        this.init_selection_url = this.element.attr('data-init-selection-url');
        this.is_sortable = this.element.attr('data-sortable') == 'true';

        // Retrieve options from the data attribute.
        var options_data = this.element.attr('data-select2-options') || {};
        if (options_data) {
            options_data =  $.parseJSON(options_data);
        }

        // Concatenate the various options.
        this.options = $.extend({}, defaults, options_data, options);

        this.set_ajax_options();

        if (! this.element.is("select")) {
            this.set_init_selection()
        }

        this.init();

        this.set_sortable();
    }

    // Set the `ajax` options of the Select2 field.  (Just below http://ivaynberg.github.io/select2/#doc-qery
    Plugin.prototype.set_ajax_options = function() {

        // If ajax options were set in the input element, merge with our defaults.
        if (this.options['ajax'] && typeof this.options['ajax'] == 'object') {
            var $el = this.element

            var defaults = {
                ajax: {
                    data: function(term, page) {
                        return {
                            q: term,
                            page: page,
                            page_limit: 10
                        };
                    },
                    results: function(data, page, query) {
                        return data;
                    }
                }
            };

            this.options = $.extend(true, defaults, this.options);
        }
    }


    Plugin.prototype.set_init_selection = function() {
        var defaults = {
            initSelection: function (element, callback) {
                var inputVal = element.val();
                if (inputVal !== '') {
                    var djselect2 = element.data('djselect2') || {};
                    var select2 = element.data('select2') || {};
                    var is_multiple = (typeof select2.opts == 'object' && select2.opts !== null) && select2.opts.multiple;

                    // If an init_selection_url exists, peform an ajax request to retrieve the values.
                    if (djselect2.init_selection_url) {
                        var data = {
                            q: inputVal
                        };
                        data['multiple'] = is_multiple ? 1 : 0;

                        $.ajax({
                            url: djselect2.init_selection_url,
                            dataType: 'json',
                            data: data,
                            success: function(data, textStatus, jqXHR) {
                                if (typeof(data) == 'object' && data.results && typeof(data.results) == 'object') {
                                    callback(data.results);
                                }
                            }
                        });
                    }
                    // No init_selection_url set so lets work with the values we have.
                    else {
                        // If multiple then split using a comma.
                        if (is_multiple) {
                            var data = [];
                            $(inputVal.split(",")).each(function () {
                                data.push({id: this, text: this});
                            });
                            callback(data);
                        }
                        // Otherwise, just set to the value of the field.
                        else {
                            callback({id: inputVal, text: inputVal});
                        }

                    }
                }
            }
        };

        this.options = $.extend(true, defaults, this.options);
    }

    Plugin.prototype.set_sortable = function() {

        if (this.is_sortable) {
            var element = this.element
            element.select2("container").find("ul.select2-choices").sortable({
                containment: 'parent',
                start: function() { element.select2("onSortStart"); },
                update: function() { element.select2("onSortEnd"); }
            });
        }

    }

    Plugin.prototype.init = function() {
        this.element.select2(this.options);
    };

    // A really lightweight plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn.extend({
        djselect2: function ( options ) {
            this.each(function () {
                if (!$.data(this, 'plugin_' + pluginName)) {
                    $.data(this, 'plugin_' + pluginName, new Plugin( this, options ));
                }
            });
            return this;
        }
    });

    // Activate each Select2 field.
    $(document).ready( function () {
        $('.django-select2').each( function (i, input) {
            var $input = $(input);
            options = {};
            $input.djselect2(options);
        });
    });

})(jQuery);



