var DjangoSelect2 = window.DjangoSelect2 || {};

(function() {

    var arrayReduce = Array.prototype.reduce;

    if (!arrayReduce) {
        arrayReduce = function(accumulator) {
            if (this === null || this === undefined) {
                throw new TypeError("Object is null or undefined");
            }
            var i = 0, l = this.length >> 0, curr;

            if (typeof accumulator !== "function") {
                // ES5 : "If IsCallable(callbackfn) is false, throw a TypeError exception."
                throw new TypeError("First argument is not callable");
            }

            if (arguments.length < 2) {
                if (l === 0) {
                    throw new TypeError("Array length is 0 and no second argument");
                }
                curr = this[0];
                i = 1; // start accumulating at the second element
            } else {
                curr = arguments[1];
            }
            while (i < l) {
                if (i in this) {
                    curr = accumulator.call(undefined, curr, this[i], i, this);
                }
                ++i;
            }

            return curr;
        };
    }

    var normalizeVersion = function(version){
        var normalized = [];
        var splits = version.split('.');
        for (var i = 0; i < splits.length; i++) {
            normalized.push(parseInt(splits[i], 10));
        }
        return normalized;
    };

    var versionCompare = function(version1, version2) {
        if ('undefined' === typeof version1) {
            throw new Error("$.versioncompare needs at least one parameter.");
        }
        version2 = version2 || $.fn.jquery;
        if (version1 == version2) return 0;

        var v1 = normalizeVersion(version1);
        var v2 = normalizeVersion(version2);
        var len = Math.max(v1.length, v2.length);
        for (var i = 0; i < len; i++) {
            v1[i] = v1[i] || 0;
            v2[i] = v2[i] || 0;
            if (v1[i] == v2[i]) continue;
            return (v1[i] > v2[i]) ? 1 : -1;
        }
        return 0;
    };

    var getBestJQuery = function() {
        var jqueries = [];
        if (typeof window.django != 'undefined' && typeof django.jQuery != 'undefined') {
            jqueries.push(['django.jQuery', django.jQuery]);
        }
        if (typeof window.jQuery != 'undefined') {
            jqueries.push(['jQuery', window.jQuery]);
        }
        if (typeof window.grp != 'undefined' && typeof grp.jQuery != 'undefined') {
            jqueries.push(['grp.jQuery', grp.jQuery]);
        }
        return arrayReduce.call(jqueries, function(prevValue, currValue, index, array) {
            return (versionCompare(currValue[1].fn.jquery, prevValue[1].fn.jquery) >= 0) ? currValue : prevValue;
        });
    };

    if (typeof(DjangoSelect2.jQuery) == 'undefined') {
        if (typeof(DjangoSelect2.versionCompare) != 'function') {
            DjangoSelect2.versionCompare = versionCompare;
        }
        var bestJQuery = getBestJQuery();
        if (versionCompare(bestJQuery[1].fn.jquery, '1.4.2') <= 0) {
            var scripts = document.getElementsByTagName("script"),
                currentScript = scripts[scripts.length-1],
                currentSrc = currentScript.src,
                rootUrl = currentSrc.replace(/\/[^\/]+$/, ''),
                newSrc = rootUrl + '/jquery-1.7.2.js';
            document.write('<scr' + 'ipt type="text/javascript" src="' + newSrc + '"></sc' + 'ript>');
        } else {
            DjangoSelect2.jQueryObj = bestJQuery[0];
            DjangoSelect2.jQuery = bestJQuery[1].noConflict();
        }
    }

})();

DjangoSelect2.onjqueryload = (function($) {
        $(document).ready(function() {
            $('.django-select2').each(function(i, input) {
                var $input = $(input);
                if (DjangoSelect2.versionCompare(DjangoSelect2.jQuery.fn.jquery, '1.4.2') <= 0) {
                    var optionsAttr = $input.attr('data-select2-options');
                    if (optionsAttr) {
                        $input.data('select2Options', $.parseJSON(optionsAttr));
                    }
                    var initSelectionUrlAttr = $input.attr('data-init-selection-url');
                    if (initSelectionUrlAttr)
                    $input.data('initSelectionUrl', initSelectionUrlAttr);
                    var sortableAttr = $input.attr('data-sortable');
                    if (sortableAttr) {
                        $input.data('sortable', (sortableAttr == 'true'));
                    }
                }

                var ajaxOptions = {
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
                    },
                    initSelection: function (element, callback) {
                        var inputVal = $input.val();
                        if (inputVal != '') {
                            var data = {
                                q: inputVal
                            };
                            var select2 = $input.data('select2') || {};
                            if (typeof select2.opts == 'object' && select2.opts !== null) {
                                data['multiple'] = (select2.opts.multiple) ? 1 : 0;
                            }
                            $.ajax({
                                url: $input.data('initSelectionUrl'),
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
                };
                var options =  $input.data('select2Options') || {};
                if (!options) {
                    options = {};
                }
                if (options['ajax'] && typeof options['ajax'] == 'object') {
                    options = $.extend(true, ajaxOptions, options);
                }
                $input.select2(options);
                var isSortable = $input.data('sortable');
                if (isSortable) {
                    $input.select2("container").find("ul.select2-choices").sortable({
                        containment: 'parent',
                        start: function() { $input.select2("onSortStart"); },
                        update: function() { $input.select2("onSortEnd"); }
                    });
                }
            });
        });
    });

if (DjangoSelect2.jQueryObj) {
    DjangoSelect2.onjqueryload(DjangoSelect2.jQuery);
}