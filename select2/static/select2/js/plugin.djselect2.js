// the semi-colon before the function invocation is a safety
// net against concatenated scripts and/or other plugins
// that are not closed properly.
;(function ( $, window, document, undefined ) {

    // undefined is used here as the undefined global
    // variable in ECMAScript 3 and is mutable (i.e. it can
    // be changed by someone else). undefined isn't really
    // being passed in so we can ensure that its value is
    // truly undefined. In ES5, undefined can no longer be
    // modified.

    // Create the defaults once
    var pluginName = 'djselect2',
        defaults = {
        propertyName: "value"
    };

    // The actual plugin constructor
    function Plugin( element, options ) {
        this.element = $(element);

        // Store this plugin on the element for later retrieval
        this.element.data('djselect2', this);

        this.init_selection_url = this.element.attr('data-init-selection-url');
        this.is_sortable = this.element.attr('data-sortable') == 'true';

        // Retrieve options from the data attribute.
        var options_data = this.element.attr('data-select2-options') || {};
        if (options_data) {
            options_data =  $.parseJSON(options_data);
        }

        // jQuery has an extend method that merges the
        // contents of two or more objects, storing the
        // result in the first object. The first object
        // is generally empty because we don't want to alter
        // the default options for future instances of the plugin
        this.options = $.extend( {}, defaults, options_data, options) ;

        this._defaults = defaults;
        this._name = pluginName;

        this.set_ajax_options()
        this.set_init_selection()

        this.init();

        this.set_sortable();
    }

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
                  results: function(data, page) {
                      return data;
                  }
              }
          };

          this.options = $.extend(true, defaults, this.options);
        }
    }


    Plugin.prototype.set_init_selection = function() {

        // If ajax options were set in the input element, merge with our defaults.
        if (this.init_selection_url) {

            var defaults = {
                initSelection: function (element, callback) {
                    var inputVal = element.val();
                    if (inputVal != '') {
                        var data = {
                            q: inputVal
                        };
                        var djselect2 = element.data('djselect2') || {};
                        var select2 = element.data('select2') || {};

                        if (djselect2.init_selection_url) {
                            if (typeof select2.opts == 'object' && select2.opts !== null) {
                                data['multiple'] = (select2.opts.multiple) ? 1 : 0;
                            }
                            $.ajax({
                                url: djselect2.init_selection_url,
                                dataType: 'json',
                                data: data,
                                success: function(data, textStatus, jqXHR) {
                                    if (typeof(data) == 'object' && typeof(data.results) == 'object' && data.results) {
                                        callback(data.results);
                                    }
                                }
                            });
                        }
                    }
                }
            };

            this.options = $.extend(true, defaults, this.options);
        }
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
        var element = this.element;
        element.select2(this.options);
    };



  // A really lightweight plugin wrapper around the constructor,
  // preventing against multiple instantiations
  $.fn[pluginName] = function ( options ) {
    return this.each(function () {
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName,
          new Plugin( this, options ));
      }
    });
  }

})( (typeof DjangoSelect2 == 'object' && DjangoSelect2.jQuery) ? DjangoSelect2.jQuery : jQuery );
