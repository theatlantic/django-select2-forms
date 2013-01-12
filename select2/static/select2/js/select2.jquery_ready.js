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
        return $.map(version.split('.'), function(value){ return parseInt(value, 10); });
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
        if (typeof window.jQuery != 'undefined') {
            jqueries.push(['jQuery', window.jQuery]);
        }
        if (typeof window.django != 'undefined' && typeof django.jQuery != 'undefined') {
            jqueries.push(['django.jQuery', django.jQuery]);
        }
        if (typeof window.grp != 'undefined' && typeof grp.jQuery != 'undefined') {
            jqueries.push(['grp.jQuery', grp.jQuery]);
        }
        return arrayReduce.call(jqueries, function(prevValue, currValue, index, array) {
            return (versionCompare(currValue[1].fn.jquery, prevValue[1].fn.jquery) >= 0) ? currValue : prevValue;
        });
    };

    if (typeof(DjangoSelect2.jQuery) == 'undefined') {
        var bestJQuery = getBestJQuery();
        DjangoSelect2.jQueryObj = bestJQuery[0];
        DjangoSelect2.jQuery = bestJQuery[1].noConflict();
    }
})();

(function($) {
    $(document).ready(function() {
        $('.django-select2').each(function(i, input) {
            var $input = $(input);
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
                        $.ajax({
                            url: $input.data('initSelectionUrl'),
                            dataType: 'json',
                            data: {
                                q: inputVal
                            },
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
})(DjangoSelect2.jQuery);